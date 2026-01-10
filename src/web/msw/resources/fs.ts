import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionSearchResponse } from '@/lib/api/fs/search'

/**
 * MSW handlers for /fs endpoints
 */
export const fsHandlers = [
  // POST /api/v1/fs/search
  http.post<never, { query: string }, SessionSearchResponse>(
    `${API_BASE_URL}/fs/search`,
    async ({ request }) => {
      const body = await request.json()
      const { query } = body

      // Mock search results based on query
      if (!query || !query.trim()) {
        return HttpResponse.json({ results: [] })
      }

      // Return mock results
      return HttpResponse.json({
        results: [
          { sessionId: 'session-1', title: `${query} - Session 1` },
          { sessionId: 'session-2', title: `${query} - Session 2` },
          { sessionId: 'session-3', title: `${query} - Session 3` }
        ]
      })
    }
  )
]
