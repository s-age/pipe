import type { ChangeEvent, KeyboardEvent, RefObject } from 'react'
import { useCallback, useMemo, useState } from 'react'

import { useFileSearchExplorerActions } from './useFileSearchExplorerActions'

export const useFileSearchExplorerHandlers = (
  inputReference?: RefObject<HTMLInputElement | null>
): {
  pathList: string[]
  query: string
  suggestions: string[]
  selectedIndex: number
  setPathList: (pathList: string[]) => void
  setQuery: (query: string) => void
  setSuggestions: (suggestions: string[]) => void
  setSelectedIndex: (index: number) => void
  handleTagDelete: (index: number) => void
  handleQueryChange: (event: ChangeEvent<HTMLInputElement>) => void
  handlePathConfirm: (path: string) => Promise<void>
  handleKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void
  handleSuggestionClick: (
    suggestion: string | { name: string; isDirectory: boolean }
  ) => void
  handleInputFocus: () => void
  actions: ReturnType<typeof useFileSearchExplorerActions>
} => {
  const [pathList, setPathList] = useState<string[]>([])
  const [query, setQuery] = useState<string>('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [rootSuggestions, setRootSuggestions] = useState<string[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)

  const actions = useFileSearchExplorerActions()

  // Create a Set of existing paths for efficient lookup
  const existingPaths = useMemo(() => new Set(pathList), [pathList])

  // Filter out already selected paths from suggestions
  const filterExistingPaths = useCallback(
    (suggestions: string[], currentPath: string[] = []): string[] =>
      suggestions.filter((suggestion) => {
        // Remove trailing slash for comparison
        const cleanSuggestion = suggestion.endsWith('/')
          ? suggestion.slice(0, -1)
          : suggestion
        const fullPath =
          currentPath.length > 0
            ? [...currentPath, cleanSuggestion].join('/')
            : cleanSuggestion

        return !existingPaths.has(fullPath)
      }),
    [existingPaths]
  )

  const loadRootSuggestionsIfNeeded = useCallback(async () => {
    if (rootSuggestions.length === 0) {
      const lsResult = await actions.getLsData({ final_path_list: [] })
      if (lsResult) {
        const rootEntries = lsResult.entries.map((entry) =>
          entry.is_dir ? `${entry.name}/` : entry.name
        )
        setRootSuggestions(rootEntries)

        return rootEntries
      }
    }

    return rootSuggestions
  }, [actions, rootSuggestions])

  const handleTagDelete = useCallback(
    (index: number): void => {
      const newPathList = pathList.filter((_, i) => i !== index)
      setPathList(newPathList)
      // Optionally trigger API call after path list changes
    },
    [pathList]
  )

  const handleQueryChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>): Promise<void> => {
      const newQuery = event.target.value
      setQuery(newQuery)
      setSelectedIndex(-1)
      // Update suggestions based on query
      if (newQuery.includes('/')) {
        const parts = newQuery.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const prefix = parts[parts.length - 1] || ''
        if (pathParts.length > 0) {
          void actions.getLsData({ final_path_list: pathParts }).then((lsResult) => {
            if (lsResult) {
              const filtered = lsResult.entries
                .filter((entry) => entry.name.startsWith(prefix))
                .map((entry) => (entry.is_dir ? `${entry.name}/` : entry.name))
              // Filter out already selected paths
              const filteredWithoutDuplicates = filterExistingPaths(filtered, pathParts)
              setSuggestions(filteredWithoutDuplicates)
            }
          })
        } else {
          // For root '/', show root suggestions
          const currentRootSuggestions = await loadRootSuggestionsIfNeeded()
          const filtered = currentRootSuggestions.filter((name) =>
            name.startsWith(prefix)
          )
          // Filter out already selected paths
          const filteredWithoutDuplicates = filterExistingPaths(filtered)
          setSuggestions(filteredWithoutDuplicates)
        }
      } else if (newQuery.length > 0) {
        // For non-slash queries, show filtered root suggestions
        const currentRootSuggestions = await loadRootSuggestionsIfNeeded()
        const filtered = currentRootSuggestions.filter((name) =>
          name.startsWith(newQuery)
        )
        // Filter out already selected paths
        const filteredWithoutDuplicates = filterExistingPaths(filtered)
        setSuggestions(filteredWithoutDuplicates)
      } else {
        setSuggestions([])
      }
    },
    [actions, loadRootSuggestionsIfNeeded, filterExistingPaths]
  )

  const handlePathConfirm = useCallback(
    async (path: string): Promise<void> => {
      // Only add if path is not empty and not already in the list
      if (path.trim() && !existingPaths.has(path)) {
        setPathList([...pathList, path])
      }
      setQuery('')
      setSuggestions([])
    },
    [pathList, existingPaths]
  )

  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      void handleQueryChange(event)
    },
    [handleQueryChange]
  )

  const handleSuggestionClick = useCallback(
    // eslint-disable-next-line react-hooks/preserve-manual-memoization
    (suggestion: string | { name: string; isDirectory: boolean }): void => {
      const suggestionName =
        typeof suggestion === 'string' ? suggestion : suggestion.name

      if (suggestionName.endsWith('/')) {
        // Directory: navigate into it
        const parts = query.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const newPathParts = [...pathParts, suggestionName.slice(0, -1)]
        const newPath = newPathParts.join('/') + '/'
        setQuery(newPath)
        // Refresh suggestions for the new directory
        void actions.getLsData({ final_path_list: newPathParts }).then((lsResult) => {
          if (lsResult) {
            const filtered = lsResult.entries.map((entry) =>
              entry.is_dir ? `${entry.name}/` : entry.name
            )
            // Filter out already selected paths
            const filteredWithoutDuplicates = filterExistingPaths(
              filtered,
              newPathParts
            )
            setSuggestions(filteredWithoutDuplicates)
          }
        })
      } else {
        // File: add to pathList only if not already present
        const parts = query.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const newPath = [...pathParts, suggestionName].join('/')

        // Check for duplicates before adding
        if (!existingPaths.has(newPath)) {
          setPathList([...pathList, newPath])
        }
        setQuery('')
        setSuggestions([])
      }
      inputReference?.current?.focus()
    },
    [query, pathList, inputReference, actions, existingPaths, filterExistingPaths]
  )

  const handleKeyDown = useCallback(
    // eslint-disable-next-line react-hooks/preserve-manual-memoization
    (event: KeyboardEvent<HTMLInputElement>): void => {
      if (suggestions.length > 0) {
        if (event.key === 'ArrowDown') {
          event.preventDefault()
          setSelectedIndex((previous) => (previous + 1) % suggestions.length)
        } else if (event.key === 'ArrowUp') {
          event.preventDefault()
          setSelectedIndex(
            (previous) => (previous - 1 + suggestions.length) % suggestions.length
          )
        } else if (event.key === 'Enter' && selectedIndex >= 0) {
          event.preventDefault()
          const selectedSuggestion = suggestions[selectedIndex]
          handleSuggestionClick(selectedSuggestion)
          inputReference?.current?.focus()
        } else if (event.key === 'Escape') {
          setSuggestions([])
          setSelectedIndex(-1)
        }
      } else if (event.key === 'Enter') {
        void handlePathConfirm(query)
      }
    },
    [
      suggestions,
      selectedIndex,
      query,
      handlePathConfirm,
      handleSuggestionClick,
      inputReference
    ]
  )

  const handleInputFocus = useCallback(async () => {
    const rootSuggestions = await loadRootSuggestionsIfNeeded()
    // Filter out already selected paths when showing suggestions on focus
    const filteredSuggestions = filterExistingPaths(rootSuggestions)
    setSuggestions(filteredSuggestions)
  }, [loadRootSuggestionsIfNeeded, filterExistingPaths])

  return {
    pathList,
    query,
    suggestions,
    selectedIndex,
    setPathList,
    setQuery,
    setSuggestions,
    setSelectedIndex,
    handleTagDelete,
    handleQueryChange: handleInputChange, // Expose InputChange
    handlePathConfirm,
    handleKeyDown,
    handleSuggestionClick,
    handleInputFocus,
    actions
  }
}
