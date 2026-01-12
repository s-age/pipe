import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { ArchiveSessionsResponse } from '@/lib/api/session_management/archiveSessions'
import type { DeleteArchivedSessionsResponse } from '@/lib/api/session_management/deleteArchivedSessions'

/**
 * MSW handlers for /session_management endpoints
 */
export const sessionManagementHandlers = [
  // POST /api/v1/session_management/archives
  http.post<never, { sessionIds: string[] }, ArchiveSessionsResponse>(
    `${API_BASE_URL}/session_management/archives`,
    async ({ request }) => {
      const { sessionIds } = await request.json()

      return HttpResponse.json({
        archivedCount: sessionIds.length,
        message: 'Sessions archived successfully',
        totalRequested: sessionIds.length
      })
    }
  ),

  // DELETE /api/v1/session_management/archives
  http.delete<
    never,
    { filePaths?: string[]; sessionIds?: string[] },
    DeleteArchivedSessionsResponse
  >(`${API_BASE_URL}/session_management/archives`, async ({ request }) => {
    const body = await request.json()
    const totalRequested =
      (body.sessionIds?.length ?? 0) + (body.filePaths?.length ?? 0)

    return HttpResponse.json({
      deletedCount: totalRequested,
      message: 'Archived sessions deleted successfully',
      totalRequested
    })
  })
]

/**
 * MSW handlers for /session_management endpoints with error responses
 */
export const sessionManagementErrorHandlers = [
  // POST /api/v1/session_management/archives (error response)
  http.post(
    `${API_BASE_URL}/session_management/archives`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to archive sessions' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // DELETE /api/v1/session_management/archives (error response)
  http.delete(
    `${API_BASE_URL}/session_management/archives`,
    () =>
      new HttpResponse(
        JSON.stringify({ message: 'Failed to delete archived sessions' }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  )
]
