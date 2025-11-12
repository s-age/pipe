import type { ChangeEvent, KeyboardEvent, RefObject } from 'react'
import { useState, useCallback, useEffect } from 'react'

import { useFileSearchExplorerActions } from './useFileSearchExplorerActions'
import { useFileSearchExplorerLifecycle } from './useFileSearchExplorerLifecycle'

export const useFileSearchExplorerHandlers = (
  inputReference?: RefObject<HTMLInputElement | null>
): {
  pathList: string[]
  query: string
  suggestions: string[]
  selectedIndex: number
  setPathList: (pathList: string[]) => void
  setQuery: (query: string) => void
  handleTagDelete: (index: number) => void
  handleQueryChange: (event: ChangeEvent<HTMLInputElement>) => void
  handlePathConfirm: (path: string) => Promise<void>
  handleKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void
  handleSuggestionClick: (
    suggestion: string | { name: string; isDirectory: boolean }
  ) => void
  actions: ReturnType<typeof useFileSearchExplorerActions>
} => {
  const [pathList, setPathList] = useState<string[]>([])
  const [query, setQuery] = useState<string>('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [rootSuggestions, setRootSuggestions] = useState<string[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)

  const actions = useFileSearchExplorerActions()

  // Load root suggestions on mount
  useEffect(() => {
    void actions.getLsData({ final_path_list: [] }).then((lsResult) => {
      if (lsResult) {
        const rootEntries = lsResult.entries.map((entry) => entry.name)
        setRootSuggestions(rootEntries)
      }
    })
  }, [actions])

  // Use lifecycle hook
  void useFileSearchExplorerLifecycle({ query, actions })

  const handleTagDelete = useCallback(
    (index: number): void => {
      const newPathList = pathList.filter((_, i) => i !== index)
      setPathList(newPathList)
      // Optionally trigger API call after path list changes
    },
    [pathList]
  )

  const handleQueryChange = useCallback(
    (newQuery: string): void => {
      console.log('handleQueryChange called with:', newQuery)
      setQuery(newQuery)
      setSelectedIndex(-1)
      // Update suggestions based on query
      if (newQuery.includes('/')) {
        console.log('includes /')
        const parts = newQuery.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const prefix = parts[parts.length - 1] || ''
        console.log('pathParts:', pathParts, 'prefix:', prefix)
        if (pathParts.length > 0) {
          console.log('calling getLsData for path')
          void actions.getLsData({ final_path_list: pathParts }).then((lsResult) => {
            console.log('getLsData result:', lsResult)
            if (lsResult) {
              const filtered = lsResult.entries
                .filter((entry) => entry.name.startsWith(prefix))
                .map((entry) => entry.name)
              console.log('filtered suggestions:', filtered)
              setSuggestions(filtered)
            }
          })
        } else {
          // For root '/', show root suggestions
          console.log('showing root suggestions')
          const filtered = rootSuggestions.filter((name) => name.startsWith(prefix))
          setSuggestions(filtered)
        }
      } else if (newQuery.length > 0) {
        // For non-slash queries, show filtered root suggestions
        console.log('showing filtered root suggestions for prefix:', newQuery)
        const filtered = rootSuggestions.filter((name) => name.startsWith(newQuery))
        setSuggestions(filtered)
      } else {
        console.log('empty query, setSuggestions([])')
        setSuggestions([])
      }
    },
    [actions, rootSuggestions]
  )

  const handlePathConfirm = useCallback(
    async (path: string): Promise<void> => {
      setPathList([...pathList, path])
      setQuery('')
      setSuggestions([])
    },
    [pathList]
  )

  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      handleQueryChange(event.target.value)
    },
    [handleQueryChange]
  )

  const handleSuggestionClick = useCallback(
    // eslint-disable-next-line react-hooks/preserve-manual-memoization
    (suggestion: string | { name: string; isDirectory: boolean }): void => {
      const suggestionName =
        typeof suggestion === 'string' ? suggestion : suggestion.name
      const parts = query.split('/')
      const pathParts = parts.slice(0, -1).filter((p) => p)
      const newPath = [...pathParts, suggestionName].join('/')
      setQuery(newPath)
      setSuggestions([])
      inputReference?.current?.focus()
    },
    [query, inputReference]
  )

  const handleKeyDown = useCallback(
    // eslint-disable-next-line react-hooks/preserve-manual-memoization
    (event: KeyboardEvent<HTMLInputElement>): void => {
      console.log('handleKeyDown:', event.key, 'selectedIndex:', selectedIndex)
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

  return {
    pathList,
    query,
    suggestions,
    selectedIndex,
    setPathList,
    setQuery,
    handleTagDelete,
    handleQueryChange: handleInputChange, // Expose InputChange
    handlePathConfirm,
    handleKeyDown,
    handleSuggestionClick,
    actions
  }
}
