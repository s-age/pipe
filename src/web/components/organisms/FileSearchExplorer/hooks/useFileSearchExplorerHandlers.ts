import type { ChangeEvent, KeyboardEvent, RefObject } from 'react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import type { BrowseResponse } from '@/lib/api/fs/browse'

import { useFileSearchExplorerActions } from './useFileSearchExplorerActions'
import { useFileSearchExplorerLifecycle } from './useFileSearchExplorerLifecycle'

type Item = {
  label: string
  value: string
  path?: string
}

type HandlersOptions = {
  existsValue: string[]
  list?: Item[]
  isMultiple: boolean
  onFocus?: () => void
  onChange?: (values: string[]) => void
}

export const useFileSearchExplorerHandlers = (
  options?: HandlersOptions
): {
  inputReference: RefObject<HTMLInputElement | null>
  suggestionListReference: RefObject<HTMLUListElement | null>
  selectedValues: string[]
  query: string
  suggestions: Item[]
  selectedIndex: number
  setSelectedValues: (values: string[]) => void
  setQuery: (query: string) => void
  setSuggestions: (suggestions: Item[]) => void
  setSelectedIndex: (index: number) => void
  handleTagDelete: (index: number) => void
  handleQueryChange: (event: ChangeEvent<HTMLInputElement>) => Promise<void>
  handleValueConfirm: (value: string) => Promise<void>
  handleKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void
  handleSuggestionClick: (suggestion: Item) => Promise<void>
  handleInputFocus: () => Promise<void>
  actions: ReturnType<typeof useFileSearchExplorerActions>
  debouncedQuery: string
} => {
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)
  const { existsValue = [], list, isMultiple = true, onFocus, onChange } = options || {}
  const [selectedValues, setSelectedValues] = useState<string[]>(existsValue)
  const [query, setQuery] = useState<string>('')
  const [suggestions, setSuggestions] = useState<Item[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)
  const focusTriggerReference = useRef<boolean>(false)

  const actions = useFileSearchExplorerActions()

  const lifecycle = useFileSearchExplorerLifecycle({
    query,
    inputReference: inputReference || { current: null },
    suggestionListReference: suggestionListReference || { current: null },
    setSuggestions,
    setSelectedIndex
  })

  // Create a Set of existing values for efficient lookup
  const existingValues = useMemo(() => new Set(selectedValues), [selectedValues])

  // Filter out already selected values from suggestions
  const filterExistingValues = useCallback(
    (suggestions: Item[]): Item[] =>
      suggestions.filter((suggestion) => !existingValues.has(suggestion.value)),
    [existingValues]
  )

  const handleTagDelete = useCallback(
    (index: number): void => {
      const newSelectedValues = selectedValues.filter((_, i) => i !== index)
      setSelectedValues(newSelectedValues)
      onChange?.(newSelectedValues)
    },
    [selectedValues, onChange]
  )

  const handleQueryChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>): Promise<void> => {
      const newQuery = event.target.value
      setQuery(newQuery)
      setSelectedIndex(-1)

      if (list) {
        // Filter from list
        const filtered = list.filter((item) =>
          item.label.toLowerCase().includes(newQuery.toLowerCase())
        )
        const filteredWithoutDuplicates = filterExistingValues(filtered)
        setSuggestions(filteredWithoutDuplicates)
      } else {
        // Use browseDirectory for file search
        if (newQuery.includes('/')) {
          const parts = newQuery.split('/')
          const pathParts = parts.slice(0, -1).filter((p) => p)
          const prefix = parts[parts.length - 1] || ''
          if (pathParts.length > 0) {
            const lsResult = await actions.browseDirectory({ finalPathList: pathParts })
            if (lsResult) {
              const filtered = lsResult.entries
                .filter((entry: BrowseResponse['entries'][number]) =>
                  entry.name.startsWith(prefix)
                )
                .map((entry: BrowseResponse['entries'][number]) => ({
                  label: entry.isDir ? `${entry.name}/` : entry.name,
                  value: entry.isDir
                    ? `${[...pathParts, entry.name].join('/')}/`
                    : [...pathParts, entry.name].join('/'),
                  path: [...pathParts, entry.name].join('/')
                }))
              const filteredWithoutDuplicates = filterExistingValues(filtered)
              setSuggestions(filteredWithoutDuplicates)
            }
          } else {
            // Root level
            const lsResult = await actions.browseDirectory({ finalPathList: [] })
            if (lsResult) {
              const filtered = lsResult.entries
                .filter((entry: BrowseResponse['entries'][number]) =>
                  entry.name.startsWith(prefix)
                )
                .map((entry: BrowseResponse['entries'][number]) => ({
                  label: entry.isDir ? `${entry.name}/` : entry.name,
                  value: entry.isDir ? `${entry.name}/` : entry.name,
                  path: entry.name
                }))
              const filteredWithoutDuplicates = filterExistingValues(filtered)
              setSuggestions(filteredWithoutDuplicates)
            }
          }
        } else if (newQuery.length > 0) {
          // Root level search
          const lsResult = await actions.browseDirectory({ finalPathList: [] })
          if (lsResult) {
            const filtered = lsResult.entries
              .filter((entry: BrowseResponse['entries'][number]) =>
                entry.name.startsWith(newQuery)
              )
              .map((entry: BrowseResponse['entries'][number]) => ({
                label: entry.isDir ? `${entry.name}/` : entry.name,
                value: entry.isDir ? `${entry.name}/` : entry.name,
                path: entry.name
              }))
            const filteredWithoutDuplicates = filterExistingValues(filtered)
            setSuggestions(filteredWithoutDuplicates)
          } else {
            setSuggestions([])
          }
        } else {
          setSuggestions([])
        }
      }
    },
    [list, actions, filterExistingValues]
  )

  const handleValueConfirm = useCallback(
    async (value: string): Promise<void> => {
      if (value.trim() && !existingValues.has(value)) {
        let newSelectedValues: string[]
        if (isMultiple) {
          newSelectedValues = [...selectedValues, value]
          setSelectedValues(newSelectedValues)
        } else {
          newSelectedValues = [value]
          setSelectedValues(newSelectedValues)
        }
        onChange?.(newSelectedValues)
      }
      setQuery('')
      setSuggestions([])
    },
    [selectedValues, existingValues, isMultiple, onChange]
  )

  const handleSuggestionClick = useCallback(
    async (suggestion: Item): Promise<void> => {
      if (suggestion.label.endsWith('/')) {
        // Directory: navigate into it
        const parts = query.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const newPathParts = [...pathParts, suggestion.label.slice(0, -1)]
        const newPath = newPathParts.join('/') + '/'
        setQuery(newPath)
        // Refresh suggestions for the new directory
        if (!list) {
          void actions
            .browseDirectory({ finalPathList: newPathParts })
            .then((lsResult) => {
              if (lsResult) {
                const filtered = lsResult.entries.map(
                  (entry: BrowseResponse['entries'][number]) => ({
                    label: entry.isDir ? `${entry.name}/` : entry.name,
                    value: entry.isDir
                      ? `${[...newPathParts, entry.name].join('/')}/`
                      : [...newPathParts, entry.name].join('/'),
                    path: [...newPathParts, entry.name].join('/')
                  })
                )
                const filteredWithoutDuplicates = filterExistingValues(filtered)
                setSuggestions(filteredWithoutDuplicates)
              }
            })
        }
      } else {
        // Item: add to selectedValues
        void handleValueConfirm(suggestion.path || suggestion.value)
      }
      focusTriggerReference.current = true
    },
    [query, actions, filterExistingValues, list, handleValueConfirm]
  )

  const handleKeyDown = useCallback(
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
          focusTriggerReference.current = true
        } else if (event.key === 'Escape') {
          setSuggestions([])
          setSelectedIndex(-1)
        }
      } else if (event.key === 'Enter') {
        void handleValueConfirm(query)
      }
    },
    [suggestions, selectedIndex, query, handleValueConfirm, handleSuggestionClick]
  )

  const handleInputFocus = useCallback(async () => {
    onFocus?.()
    if (!list) {
      // Load root suggestions for file search
      const lsResult = await actions.browseDirectory({ finalPathList: [] })
      if (lsResult) {
        const filtered = lsResult.entries.map(
          (entry: BrowseResponse['entries'][number]) => ({
            label: entry.isDir ? `${entry.name}/` : entry.name,
            value: entry.isDir ? `${entry.name}/` : entry.name,
            path: entry.name
          })
        )
        const filteredWithoutDuplicates = filterExistingValues(filtered)
        setSuggestions(filteredWithoutDuplicates)
      }
    } else {
      // Show filtered list
      const filteredWithoutDuplicates = filterExistingValues(list)
      setSuggestions(filteredWithoutDuplicates)
    }
  }, [list, actions, filterExistingValues, onFocus])

  // Focus the input when focusTrigger changes
  useEffect(() => {
    if (focusTriggerReference.current) {
      inputReference?.current?.focus()
      focusTriggerReference.current = false
    }
  }, [inputReference])

  return {
    inputReference,
    suggestionListReference,
    selectedValues,
    query,
    suggestions,
    selectedIndex,
    setSelectedValues,
    setQuery,
    setSuggestions,
    setSelectedIndex,
    handleTagDelete,
    handleQueryChange,
    handleValueConfirm,
    handleKeyDown,
    handleSuggestionClick,
    handleInputFocus,
    actions,
    debouncedQuery: lifecycle.debouncedQuery
  }
}
