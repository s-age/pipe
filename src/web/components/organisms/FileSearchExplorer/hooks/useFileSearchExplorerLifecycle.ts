import { useEffect, useMemo, useState } from 'react'

type Item = {
  label: string
  value: string
  path?: string
}

type UseFileSearchExplorerLifecycleProperties = {
  inputReference: React.RefObject<HTMLInputElement | null>
  query: string
  selectedValues: string[]
  suggestionListReference: React.RefObject<HTMLUListElement | null>
  setSelectedIndex: (index: number) => void
  setSuggestions: (suggestions: Item[]) => void
  // ... cache management state/setters
}

export const useFileSearchExplorerLifecycle = ({
  inputReference,
  query,
  selectedValues,
  suggestionListReference,
  setSelectedIndex,
  setSuggestions
}: UseFileSearchExplorerLifecycleProperties): {
  debouncedQuery: string
  existingValues: Set<string>
} => {
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query)

  const existingValues = useMemo(() => new Set(selectedValues), [selectedValues])

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
    debouncedQuery,
    existingValues
  }
}
