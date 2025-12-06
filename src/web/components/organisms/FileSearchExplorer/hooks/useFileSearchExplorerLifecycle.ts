import { useEffect, useState } from 'react'

import type { useFileSearchExplorerActions } from './useFileSearchExplorerActions'

type Item = {
  label: string
  value: string
  path?: string
}

type UseFileSearchExplorerLifecycleProperties = {
  query: string
  actions: ReturnType<typeof useFileSearchExplorerActions>
  inputReference: React.RefObject<HTMLInputElement | null>
  suggestionListReference: React.RefObject<HTMLUListElement | null>
  setSuggestions: (suggestions: Item[]) => void
  setSelectedIndex: (index: number) => void
  // ... cache management state/setters
}

export const useFileSearchExplorerLifecycle = ({
  query,
  actions,
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

  // Monitor changes in debouncedQuery and trigger API call
  useEffect((): void => {
    if (debouncedQuery) {
      // Call searchL2 API here
      void actions.searchFiles({ query: debouncedQuery, path: '' }) // Set appropriate path
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

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
