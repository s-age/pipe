import type { ChangeEvent, KeyboardEvent, RefObject } from 'react'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { useFileSearchExplorerActions } from './useFileSearchExplorerActions'

type Item = {
  label: string
  value: string
  path?: string
}

type HandlersOptions = {
  existsValue: string[]
  list?: Item[]
  isMultiple: boolean
}

export const useFileSearchExplorerHandlers = (
  inputReference?: RefObject<HTMLInputElement | null>,
  options?: HandlersOptions
): {
  selectedValues: string[]
  query: string
  suggestions: Item[]
  selectedIndex: number
  setSelectedValues: (values: string[]) => void
  setQuery: (query: string) => void
  setSuggestions: (suggestions: Item[]) => void
  setSelectedIndex: (index: number) => void
  handleTagDelete: (index: number) => void
  handleQueryChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleValueConfirm: (value: string) => Promise<void>
  handleKeyDown: (event: KeyboardEvent<HTMLInputElement>) => void
  handleSuggestionClick: (suggestion: Item) => void
  handleInputFocus: () => void
  actions: ReturnType<typeof useFileSearchExplorerActions>
} => {
  const { existsValue = [], list, isMultiple = true } = options || {}
  const [selectedValues, setSelectedValues] = useState<string[]>(existsValue)
  const [query, setQuery] = useState<string>('')
  const [suggestions, setSuggestions] = useState<Item[]>([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)
  const [focusTrigger, setFocusTrigger] = useState<number>(0)

  const actions = useFileSearchExplorerActions()

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
    },
    [selectedValues]
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
        // Use getLsData for file search
        if (newQuery.includes('/')) {
          const parts = newQuery.split('/')
          const pathParts = parts.slice(0, -1).filter((p) => p)
          const prefix = parts[parts.length - 1] || ''
          if (pathParts.length > 0) {
            void actions.getLsData({ final_path_list: pathParts }).then((lsResult) => {
              if (lsResult) {
                const filtered = lsResult.entries
                  .filter((entry) => entry.name.startsWith(prefix))
                  .map((entry) => ({
                    label: entry.is_dir ? `${entry.name}/` : entry.name,
                    value: entry.is_dir ? `${entry.name}/` : entry.name,
                    path: [...pathParts, entry.name].join('/')
                  }))
                const filteredWithoutDuplicates = filterExistingValues(filtered)
                setSuggestions(filteredWithoutDuplicates)
              }
            })
          } else {
            // Root level
            void actions.getLsData({ final_path_list: [] }).then((lsResult) => {
              if (lsResult) {
                const filtered = lsResult.entries
                  .filter((entry) => entry.name.startsWith(prefix))
                  .map((entry) => ({
                    label: entry.is_dir ? `${entry.name}/` : entry.name,
                    value: entry.is_dir ? `${entry.name}/` : entry.name,
                    path: entry.name
                  }))
                const filteredWithoutDuplicates = filterExistingValues(filtered)
                setSuggestions(filteredWithoutDuplicates)
              }
            })
          }
        } else if (newQuery.length > 0) {
          // Root level search
          void actions.getLsData({ final_path_list: [] }).then((lsResult) => {
            if (lsResult) {
              const filtered = lsResult.entries
                .filter((entry) => entry.name.startsWith(newQuery))
                .map((entry) => ({
                  label: entry.is_dir ? `${entry.name}/` : entry.name,
                  value: entry.is_dir ? `${entry.name}/` : entry.name,
                  path: entry.name
                }))
              const filteredWithoutDuplicates = filterExistingValues(filtered)
              setSuggestions(filteredWithoutDuplicates)
            }
          })
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
        if (isMultiple) {
          setSelectedValues([...selectedValues, value])
        } else {
          setSelectedValues([value])
        }
      }
      setQuery('')
      setSuggestions([])
    },
    [selectedValues, existingValues, isMultiple]
  )

  const handleSuggestionClick = useCallback(
    (suggestion: Item): void => {
      if (suggestion.label.endsWith('/')) {
        // Directory: navigate into it
        const parts = query.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const newPathParts = [...pathParts, suggestion.label.slice(0, -1)]
        const newPath = newPathParts.join('/') + '/'
        setQuery(newPath)
        // Refresh suggestions for the new directory
        if (!list) {
          void actions.getLsData({ final_path_list: newPathParts }).then((lsResult) => {
            if (lsResult) {
              const filtered = lsResult.entries.map((entry) => ({
                label: entry.is_dir ? `${entry.name}/` : entry.name,
                value: entry.is_dir ? `${entry.name}/` : entry.name,
                path: [...newPathParts, entry.name].join('/')
              }))
              const filteredWithoutDuplicates = filterExistingValues(filtered)
              setSuggestions(filteredWithoutDuplicates)
            }
          })
        }
      } else {
        // Item: add to selectedValues
        void handleValueConfirm(suggestion.value)
      }
      setFocusTrigger((previous) => previous + 1)
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
          setFocusTrigger((previous) => previous + 1)
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
    if (!list) {
      // Load root suggestions for file search
      const lsResult = await actions.getLsData({ final_path_list: [] })
      if (lsResult) {
        const filtered = lsResult.entries.map((entry) => ({
          label: entry.is_dir ? `${entry.name}/` : entry.name,
          value: entry.is_dir ? `${entry.name}/` : entry.name,
          path: entry.name
        }))
        const filteredWithoutDuplicates = filterExistingValues(filtered)
        setSuggestions(filteredWithoutDuplicates)
      }
    } else {
      // Show filtered list
      const filteredWithoutDuplicates = filterExistingValues(list)
      setSuggestions(filteredWithoutDuplicates)
    }
  }, [list, actions, filterExistingValues])

  // Focus the input when focusTrigger changes
  useEffect(() => {
    if (focusTrigger > 0) {
      inputReference?.current?.focus()
    }
  }, [focusTrigger, inputReference])

  return {
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
    actions
  }
}
