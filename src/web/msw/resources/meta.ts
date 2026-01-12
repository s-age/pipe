import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { EditHyperparametersRequest } from '@/lib/api/meta/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Reference } from '@/types/reference'

/**
 * MSW handlers for /meta endpoints
 */
export const metaHandlers = [
  // PATCH /api/v1/session/:sessionId/hyperparameters
  http.patch<
    { sessionId: string },
    EditHyperparametersRequest,
    { message: string; session: SessionDetail }
  >(`${API_BASE_URL}/session/:sessionId/hyperparameters`, async ({ params }) =>
    HttpResponse.json({
      message: 'Hyperparameters updated successfully',
      session: {
        sessionId: params.sessionId as string,
        hyperparameters: {
          temperature: 0.7,
          topP: 0.9,
          topK: 5
        }
      } as SessionDetail
    })
  ),

  // POST /api/v1/meta/hyperparameters/:sessionId (Legacy/Other)
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
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/persist
  http.patch<
    { sessionId: string; referenceIndex: string },
    { persist: boolean },
    { message: string }
  >(`${API_BASE_URL}/session/:sessionId/references/:referenceIndex/persist`, () =>
    HttpResponse.json({
      message: 'Reference persist state updated successfully'
    })
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/ttl
  http.patch<
    { sessionId: string; referenceIndex: string },
    { ttl: number },
    { message: string }
  >(`${API_BASE_URL}/session/:sessionId/references/:referenceIndex/ttl`, () =>
    HttpResponse.json({
      message: 'Reference TTL updated successfully'
    })
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/toggle
  http.patch<{ sessionId: string; referenceIndex: string }, never, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/references/:referenceIndex/toggle`,
    () =>
      HttpResponse.json({
        message: 'Reference disabled state updated successfully'
      })
  )
]

/**
 * MSW handlers for /meta endpoints with error responses
 */
export const metaErrorHandlers = [
  // PATCH /api/v1/session/:sessionId/hyperparameters (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/hyperparameters`,
    () =>
      new HttpResponse(
        JSON.stringify({ message: 'Failed to update hyperparameters' }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  ),

  // PATCH /api/v1/session/:sessionId/references (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/references`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to add reference.' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/persist (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/references/:referenceIndex/persist`,
    () =>
      HttpResponse.json(
        { message: 'Failed to update reference persist state.' },
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/ttl (error response)
  http.patch(`${API_BASE_URL}/session/:sessionId/references/:referenceIndex/ttl`, () =>
    HttpResponse.json(
      { message: 'Failed to update reference TTL.' },
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  ),

  // PATCH /api/v1/session/:sessionId/references/:referenceIndex/toggle (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/references/:referenceIndex/toggle`,
    () =>
      HttpResponse.json(
        { message: 'Failed to update reference disabled state.' },
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  )
]
