import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { Reference } from '@/types/reference'

/**
 * MSW handlers for /meta endpoints
 */
export const metaHandlers = [
  // POST /api/v1/meta/hyperparameters/:sessionId
  http.post(`${API_BASE_URL}/meta/hyperparameters/:sessionId`, async ({ params }) =>
    HttpResponse.json({
      message: 'Hyperparameters updated successfully',
      session: {
        sessionId: params.sessionId as string,
        hyperparameters: {
          temperature: 0.7,
          topP: 0.9,
          topK: 5
        }
      }
    })
  ),

  // PATCH /api/v1/session/:sessionId/references
  http.patch<{ sessionId: string }, { references: Reference[] }, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/references`,
    () =>
      HttpResponse.json({
        message: 'Reference added successfully'
      })
  )
]

/**
 * MSW handlers for /meta endpoints with error responses
 */
export const metaErrorHandlers = [
  // PATCH /api/v1/session/:sessionId/references (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/references`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to add reference.' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
