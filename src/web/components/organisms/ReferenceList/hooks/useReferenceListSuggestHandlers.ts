import { useCallback, useMemo, useRef, useState } from 'react'

import type { Reference } from '@/types/reference'

import { useReferenceListSuggestLifecycle } from './useReferenceListSuggestLifecycle'

export const useReferenceListSuggestHandlers = (
  actions: {
    loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
    loadSubDirectorySuggestions: (
      pathParts: string[]
    ) => Promise<{ name: string; isDirectory: boolean }[]>
    addReference: (path: string) => Promise<void>
  },
  existingReferences: Reference[]
): {
  inputValue: string
  suggestions: { name: string; isDirectory: boolean }[]
  selectedIndex: number
  inputReference: React.RefObject<HTMLInputElement | null>
  suggestionListReference: React.RefObject<HTMLUListElement | null>
  handleFocus: () => Promise<void>
  handleInputChange: (event: React.ChangeEvent<HTMLInputElement>) => Promise<void>
  handleKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => Promise<void>
  handleSuggestionClick: (
    suggestion: string | { name: string; isDirectory: boolean }
  ) => Promise<void>
} => {
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState<
    { name: string; isDirectory: boolean }[]
  >([])
  const [rootSuggestions, setRootSuggestions] = useState<
    { name: string; isDirectory: boolean }[]
  >([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)

  // Get paths of existing references for filtering
  const existingPaths = useMemo(
    () => new Set(existingReferences.map((reference) => reference.path)),
    [existingReferences]
  )

  // Lifecycle: click outside detection
  useReferenceListSuggestLifecycle({
    inputReference,
    suggestionListReference,
    setSuggestions,
    setSelectedIndex
  })

  const handleFocus = useCallback(async (): Promise<void> => {
    if (rootSuggestions.length === 0) {
      const suggestions = await actions.loadRootSuggestions()
      // Filter out already selected references when loading for the first time
      const filteredSuggestions = suggestions.filter(
        (suggestion) => !existingPaths.has(suggestion.name)
      )
      setRootSuggestions(filteredSuggestions)
      setSuggestions(filteredSuggestions)
    } else {
      // Filter out already selected references from cached rootSuggestions
      const filteredSuggestions = rootSuggestions.filter(
        (suggestion) => !existingPaths.has(suggestion.name)
      )
      setSuggestions(filteredSuggestions)
    }
    setSelectedIndex(-1)
  }, [actions, rootSuggestions, existingPaths])

  const handleInputChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      const value = event.target.value
      setInputValue(value)

      if (value.trim() === '') {
        // Filter out already selected references
        const filteredSuggestions = rootSuggestions.filter(
          (suggestion) => !existingPaths.has(suggestion.name)
        )
        setSuggestions(filteredSuggestions)
        setSelectedIndex(-1)

        return
      }

      const pathParts = value.split('/').filter((part) => part !== '')
      const lastPart = pathParts[pathParts.length - 1] || ''

      if (pathParts.length === 1) {
        // Root level suggestions
        const filteredSuggestions = rootSuggestions.filter((suggestion) =>
          suggestion.name.toLowerCase().startsWith(lastPart.toLowerCase())
        )
        // Filter out already selected references
        const finalSuggestions = filteredSuggestions.filter(
          (suggestion) => !existingPaths.has(suggestion.name)
        )
        setSuggestions(finalSuggestions)
        setSelectedIndex(-1)
      } else {
        // Subdirectory suggestions
        const parentPathParts = pathParts.slice(0, -1)
        const subSuggestions =
          await actions.loadSubDirectorySuggestions(parentPathParts)
        const filteredSuggestions = subSuggestions.filter((suggestion) =>
          suggestion.name.toLowerCase().startsWith(lastPart.toLowerCase())
        )
        // Filter out already selected references (full path)
        const currentPath = parentPathParts.join('/')
        const finalSuggestions = filteredSuggestions.filter(
          (suggestion) => !existingPaths.has(`${currentPath}/${suggestion.name}`)
        )
        setSuggestions(finalSuggestions)
        setSelectedIndex(-1)
      }
    },
    [actions, rootSuggestions, existingPaths]
  )

  const handleSuggestionClick = useCallback(
    async (
      suggestion: string | { name: string; isDirectory: boolean }
    ): Promise<void> => {
      const suggestionName =
        typeof suggestion === 'string' ? suggestion : suggestion.name
      const isDirectory =
        typeof suggestion === 'string' ? false : suggestion.isDirectory

      if (inputValue.includes('/')) {
        const pathParts = inputValue.split('/')
        pathParts[pathParts.length - 1] = suggestionName
        const newPath = pathParts.join('/')

        if (isDirectory) {
          setInputValue(newPath + '/')
          // Load subdirectory suggestions
          const subSuggestions = await actions.loadSubDirectorySuggestions(
            newPath.split('/').filter((part) => part !== '')
          )
          // Filter out already selected references
          const filteredSuggestions = subSuggestions.filter(
            (subSuggestion) => !existingPaths.has(`${newPath}/${subSuggestion.name}`)
          )
          setSuggestions(filteredSuggestions)
          setSelectedIndex(-1)
        } else {
          // Only add files, not directories
          setInputValue(newPath)
          void actions.addReference(newPath)
          setInputValue('')
          setSuggestions([])
          setSelectedIndex(-1)
        }
      } else {
        if (isDirectory) {
          setInputValue(suggestionName + '/')
          // Load subdirectory suggestions
          const subSuggestions = await actions.loadSubDirectorySuggestions([
            suggestionName
          ])
          // Filter out already selected references
          const filteredSuggestions = subSuggestions.filter(
            (subSuggestion) =>
              !existingPaths.has(`${suggestionName}/${subSuggestion.name}`)
          )
          setSuggestions(filteredSuggestions)
          setSelectedIndex(-1)
        } else {
          // Only add files, not directories
          setInputValue(suggestionName)
          void actions.addReference(suggestionName)
          setInputValue('')
          setSuggestions([])
          setSelectedIndex(-1)
        }
      }
    },
    [inputValue, actions, existingPaths]
  )

  const handleKeyDown = useCallback(
    async (event: React.KeyboardEvent<HTMLInputElement>): Promise<void> => {
      if (suggestions.length === 0) return

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          setSelectedIndex((previousIndex) =>
            previousIndex < suggestions.length - 1 ? previousIndex + 1 : 0
          )
          break
        case 'ArrowUp':
          event.preventDefault()
          setSelectedIndex((previousIndex) =>
            previousIndex > 0 ? previousIndex - 1 : suggestions.length - 1
          )
          break
        case 'Enter':
          event.preventDefault()
          if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
            const selectedSuggestion = suggestions[selectedIndex]
            // Only submit files from suggestions, not directories
            if (!selectedSuggestion.isDirectory) {
              await handleSuggestionClick(selectedSuggestion)
            } else {
              // For directories, just navigate into them
              await handleSuggestionClick(selectedSuggestion)
            }
          } else {
            // Don't allow direct submission of paths not in suggestions
            // User must select from suggestions to ensure the file exists
          }
          break
        case 'Escape':
          setSuggestions([])
          setSelectedIndex(-1)
          break
      }
    },
    [suggestions, selectedIndex, handleSuggestionClick]
  )

  return {
    inputValue,
    suggestions,
    selectedIndex,
    inputReference,
    suggestionListReference,
    handleFocus,
    handleInputChange,
    handleKeyDown,
    handleSuggestionClick
  }
}
