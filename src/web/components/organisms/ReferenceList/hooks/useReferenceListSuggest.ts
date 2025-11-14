import { useCallback, useEffect, useRef, useState } from 'react'

export const useReferenceListSuggest = (actions: {
  loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
  loadSubDirectorySuggestions: (
    pathParts: string[]
  ) => Promise<{ name: string; isDirectory: boolean }[]>
  addReference: (path: string) => Promise<void>
}): {
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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (
        inputReference.current &&
        suggestionListReference.current &&
        !inputReference.current.contains(event.target as Node) &&
        !suggestionListReference.current.contains(event.target as Node)
      ) {
        setSuggestions([])
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return (): void => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleFocus = useCallback(async (): Promise<void> => {
    if (rootSuggestions.length === 0) {
      const suggestions = await actions.loadRootSuggestions()
      setRootSuggestions(suggestions)
    }
    setSuggestions(rootSuggestions)
    setSelectedIndex(-1)
  }, [actions, rootSuggestions])

  const handleInputChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      const value = event.target.value
      setInputValue(value)

      if (value.trim() === '') {
        setSuggestions(rootSuggestions)
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
        setSuggestions(filteredSuggestions)
        setSelectedIndex(-1)
      } else {
        // Subdirectory suggestions
        const parentPathParts = pathParts.slice(0, -1)
        const subSuggestions =
          await actions.loadSubDirectorySuggestions(parentPathParts)
        const filteredSuggestions = subSuggestions.filter((suggestion) =>
          suggestion.name.toLowerCase().startsWith(lastPart.toLowerCase())
        )
        setSuggestions(filteredSuggestions)
        setSelectedIndex(-1)
      }
    },
    [actions, rootSuggestions]
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
          const subPathParts = newPath.split('/').filter((part) => part !== '')
          const subSuggestions = await actions.loadSubDirectorySuggestions(subPathParts)
          setSuggestions(subSuggestions)
          setSelectedIndex(-1)
        } else {
          setInputValue(newPath)
          await actions.addReference(newPath)
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
          setSuggestions(subSuggestions)
          setSelectedIndex(-1)
        } else {
          setInputValue(suggestionName)
          await actions.addReference(suggestionName)
          setInputValue('')
          setSuggestions([])
          setSelectedIndex(-1)
        }
      }
    },
    [inputValue, actions]
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
            await handleSuggestionClick(suggestions[selectedIndex])
          } else {
            await actions.addReference(inputValue)
            setInputValue('')
            setSuggestions([])
            setSelectedIndex(-1)
          }
          break
        case 'Escape':
          setSuggestions([])
          setSelectedIndex(-1)
          break
      }
    },
    [suggestions, selectedIndex, inputValue, actions, handleSuggestionClick]
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
