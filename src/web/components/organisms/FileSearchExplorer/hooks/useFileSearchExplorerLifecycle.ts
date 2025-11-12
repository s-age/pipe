import { useEffect, useState } from 'react'

import type { useFileSearchExplorerActions } from './useFileSearchExplorerActions'

type UseFileSearchExplorerLifecycleProperties = {
  query: string
  actions: ReturnType<typeof useFileSearchExplorerActions>
  // ... cache management state/setters
}

export const useFileSearchExplorerLifecycle = ({
  query,
  actions
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
      void actions.searchL2({ query: debouncedQuery, path: '' }) // Set appropriate path
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return {
    debouncedQuery
  }
}
