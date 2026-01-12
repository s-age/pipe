import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type {
  BrowseRequest,
  BrowseResponse,
  FileSearchRequest,
  FileSearchResponse
} from '@/lib/api/fs/browse'
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
  ),

  // POST /api/v1/fs/browse_l2
  http.post<never, FileSearchRequest, FileSearchResponse>(
    `${API_BASE_URL}/fs/browse_l2`,
    async ({ request }) => {
      const { query } = await request.json()
      return HttpResponse.json({
        results: [
          {
            filePath: 'src/test.ts',
            lineContent: `found ${query}`,
            lineNumber: 10
          }
        ]
      })
    }
  ),

  // POST /api/v1/fs/browse
  http.post<never, BrowseRequest, BrowseResponse>(
    `${API_BASE_URL}/fs/browse`,
    async ({ request }) => {
      const { finalPathList } = await request.json()
      const path = finalPathList.join('/')
      return HttpResponse.json({
        entries: [
          {
            isDir: true,
            name: 'subdir',
            path: `${path}/subdir`
          },
          {
            isDir: false,
            name: 'file.txt',
            path: `${path}/file.txt`,
            size: 1024
          }
        ]
      })
    }
  )
]

/**
 * MSW handlers for /fs endpoints with error responses
 */
export const fsErrorHandlers = [
  // POST /api/v1/fs/browse_l2 (error response)
  http.post(`${API_BASE_URL}/fs/browse_l2`, () => {
    return new HttpResponse(JSON.stringify({ message: 'Search failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }),

  // POST /api/v1/fs/browse (error response)
  http.post(`${API_BASE_URL}/fs/browse`, () => {
    return new HttpResponse(JSON.stringify({ message: 'Failed to list directory' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  })
]
