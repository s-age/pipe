import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'

/**
 * MSW handlers for /turn endpoints
 */
export const turnHandlers = [
  // DELETE /api/v1/session/:sessionId/turn/:turnIndex
  http.delete<{ sessionId: string; turnIndex: string }, never, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () =>
      HttpResponse.json({
        message: 'Turn deleted successfully'
      })
  ),

  // PATCH /api/v1/session/:sessionId/turn/:turnIndex
  http.patch<
    { sessionId: string; turnIndex: string },
    Record<string, unknown>,
    { message: string }
  >(`${API_BASE_URL}/session/:sessionId/turn/:turnIndex`, async ({ request }) => {
    await request.json()

    return HttpResponse.json({
      message: 'Turn updated successfully'
    })
  }),

  // POST /api/v1/session/:sessionId/fork/:forkIndex
  http.post<{ sessionId: string; forkIndex: string }, never, { newSessionId: string }>(
    `${API_BASE_URL}/session/:sessionId/fork/:forkIndex`,
    ({ params }) =>
      HttpResponse.json({
        newSessionId: `forked-session-${params.sessionId}`
      })
  )
]

/**
 * MSW handlers for /turn endpoints with error responses
 */
export const turnErrorHandlers = [
  // DELETE /api/v1/session/:sessionId/turn/:turnIndex (error response)
  http.delete(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to delete turn' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // PATCH /api/v1/session/:sessionId/turn/:turnIndex (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to update turn' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/session/:sessionId/fork/:forkIndex (error response)
  http.post(
    `${API_BASE_URL}/session/:sessionId/fork/:forkIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to fork session' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
