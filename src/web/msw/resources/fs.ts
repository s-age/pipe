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
  ),

  // GET /api/v1/fs/procedures
  http.get(`${API_BASE_URL}/fs/procedures`, () =>
    HttpResponse.json({
      procedures: [
        { label: 'Procedure 1', value: 'proc-1' },
        { label: 'Procedure 2', value: 'proc-2' },
        { label: 'Procedure 3', value: 'proc-3' }
      ]
    })
  ),

  // GET /api/v1/fs/roles
  http.get(`${API_BASE_URL}/fs/roles`, () =>
    HttpResponse.json({
      roles: [
        { label: 'Admin', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'Viewer', value: 'viewer' }
      ]
    })
  )
]
