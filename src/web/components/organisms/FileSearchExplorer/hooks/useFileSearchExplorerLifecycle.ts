import { useEffect, useState } from 'react'

type Item = {
  label: string
  value: string
  path?: string
}

type UseFileSearchExplorerLifecycleProperties = {
  query: string
  inputReference: React.RefObject<HTMLInputElement | null>
  suggestionListReference: React.RefObject<HTMLUListElement | null>
  setSuggestions: (suggestions: Item[]) => void
  setSelectedIndex: (index: number) => void
  // ... cache management state/setters
}

export const useFileSearchExplorerLifecycle = ({
  query,
  inputReference,
  suggestionListReference,
  setSuggestions,
  setSelectedIndex
}: UseFileSearchExplorerLifecycleProperties): {
  debouncedQuery: string
} => {
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query)

  // Debounce processing
  useEffect((): (() => void) => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300) // 300ms debounce

    return () => {
      clearTimeout(handler)
    }
  }, [query])

  // Close suggestions when clicking outside
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
  }, [inputReference, suggestionListReference, setSuggestions, setSelectedIndex])

  return {
    debouncedQuery
  }
}
