import { useCallback, useEffect, useRef, useState } from 'react'

export const useReferenceListHandlers = (actions: {
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
  handleAdd: () => Promise<void>
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

  const handleFocus = useCallback(async () => {
    if (rootSuggestions.length === 0) {
      const rootEntries = await actions.loadRootSuggestions()
      setRootSuggestions(rootEntries)
    }
  }, [actions, rootSuggestions.length])

  const handleInputChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value
      setInputValue(value)
      setSelectedIndex(-1)
      if (value.includes('/')) {
        const parts = value.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const prefix = parts[parts.length - 1] || ''
        if (pathParts.length > 0) {
          const entries = await actions.loadSubDirectorySuggestions(pathParts)
          const filtered = entries.filter((entry) => entry.name.startsWith(prefix))
          setSuggestions(filtered)
        } else {
          const filtered = rootSuggestions.filter((item) =>
            item.name.startsWith(prefix)
          )
          setSuggestions(filtered)
        }
      } else if (value.length > 0) {
        const filtered = rootSuggestions.filter((item) => item.name.startsWith(value))
        setSuggestions(filtered)
      } else {
        setSuggestions([])
      }
    },
    [actions, rootSuggestions]
  )

  const handleKeyDown = useCallback(
    async (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (suggestions.length === 0) return
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setSelectedIndex((previous) => (previous + 1) % suggestions.length)
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setSelectedIndex(
          (previous) => (previous - 1 + suggestions.length) % suggestions.length
        )
      } else if (event.key === 'Enter') {
        event.preventDefault()
        if (selectedIndex >= 0) {
          const selected = suggestions[selectedIndex]
          if (selected.isDirectory) {
            const newPath = `${inputValue.split('/').slice(0, -1).join('/')}/${selected.name}/`
            setInputValue(newPath)
            const pathParts = newPath.split('/').filter((p) => p)
            const entries = await actions.loadSubDirectorySuggestions(pathParts)
            setSuggestions(entries)
          } else {
            // ファイルが選択された場合は直接参照を追加
            await actions.addReference(selected.name)
            setInputValue('')
            setSuggestions([])
          }
          setSelectedIndex(-1)
        } else if (inputValue.trim()) {
          // 補完候補が選択されていないがinputに値がある場合はAddと同じ動作
          await actions.addReference(inputValue.trim())
          setInputValue('')
          setSuggestions([])
        }
      } else if (event.key === 'Escape') {
        event.preventDefault()
        setSuggestions([])
        setSelectedIndex(-1)
      }
    },
    [suggestions, selectedIndex, inputValue, actions]
  )

  const handleSuggestionClick = useCallback(
    async (suggestion: string | { name: string; isDirectory: boolean }) => {
      if (typeof suggestion === 'string') {
        setInputValue(suggestion)
      } else {
        if (suggestion.isDirectory) {
          const newPath = `${inputValue.split('/').slice(0, -1).join('/')}/${suggestion.name}/`
          setInputValue(newPath)
          const pathParts = newPath.split('/').filter((p) => p)
          const entries = await actions.loadSubDirectorySuggestions(pathParts)
          setSuggestions(entries)
        } else {
          setInputValue(suggestion.name)
        }
      }
      setSelectedIndex(-1)
    },
    [inputValue, actions]
  )

  const handleAdd = useCallback(async () => {
    if (inputValue.trim()) {
      await actions.addReference(inputValue.trim())
      setInputValue('')
      setSuggestions([])
      setSelectedIndex(-1)
    }
  }, [inputValue, actions])

  return {
    inputValue,
    suggestions,
    selectedIndex,
    inputReference,
    suggestionListReference,
    handleFocus,
    handleInputChange,
    handleKeyDown,
    handleSuggestionClick,
    handleAdd
  }
}
