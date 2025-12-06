import { useCallback } from 'react'

import { searchSessions } from '@/lib/api/search/searchSessions'
import { addToast } from '@/stores/useToastStore'

type SearchResult = {
  sessionId: string
  title: string
}

export const useSearchSessionsActions = (): {
  executeSearch: (q: string) => Promise<SearchResult[]>
} => {
  const executeSearch = useCallback(async (q: string): Promise<SearchResult[]> => {
    try {
      const data = await searchSessions({ query: q })

      return Array.isArray(data.results) ? data.results : []
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Search failed'
      })

      return []
    }
  }, [])

  return { executeSearch }
}
