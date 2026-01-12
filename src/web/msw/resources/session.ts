import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionDetail } from '@/lib/api/session/getSession'

/**
 * MSW handlers for /session endpoints
 */
export const sessionHandlers = [
  // GET /api/v1/session/:sessionId
  http.get<{ sessionId: string }, never, SessionDetail>(
    `${API_BASE_URL}/session/:sessionId`,
    ({ params }) => {
      const mockSessionDetail: SessionDetail = {
        sessionId: params.sessionId,
        purpose: 'Test Purpose',
        background: 'Test Background',
        instruction: 'Test Instruction',
        artifacts: [],
        roles: [],
        references: [],
        hyperparameters: null,
        multiStepReasoningEnabled: false,
        parent: null,
        procedure: null,
        turns: [],
        todos: [
          { title: 'Todo 1', checked: false },
          { title: 'Todo 2', checked: true }
        ]
      }

      return HttpResponse.json(mockSessionDetail)
    }
  ),

  // PATCH /api/v1/session/:sessionId/meta
  http.patch(`${API_BASE_URL}/session/:sessionId/meta`, () =>
    HttpResponse.json({ message: 'Session metadata saved' })
  ),

  // PATCH /api/v1/session/:sessionId/multi_step_reasoning
  http.patch(
    `${API_BASE_URL}/session/:sessionId/multi_step_reasoning`,
    async ({ request }) => {
      const body = await request.json()

      return HttpResponse.json({
        message: 'Multi-step reasoning updated',
        session: {
          multiStepReasoningEnabled: (body as { multiStepReasoningEnabled: boolean })
            .multiStepReasoningEnabled
        }
      })
    }
  ),

  // PATCH /api/v1/session/:sessionId/references/:index/persist
  http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/persist`, () =>
    HttpResponse.json({ message: 'Success' })
  ),

  // PATCH /api/v1/session/:sessionId/references/:index/ttl
  http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/ttl`, () =>
    HttpResponse.json({ message: 'Success' })
  ),

  // PATCH /api/v1/session/:sessionId/references/:index/toggle
  http.patch(`${API_BASE_URL}/session/:sessionId/references/:index/toggle`, () =>
    HttpResponse.json({
      disabled: true,
      message: 'Success'
    })
  ),

  // PATCH /api/v1/session/:sessionId/todos
  http.patch(`${API_BASE_URL}/session/:sessionId/todos`, () =>
    HttpResponse.json({ message: 'Todos updated' })
  ),

  // DELETE /api/v1/session/:sessionId/todos
  http.delete(`${API_BASE_URL}/session/:sessionId/todos`, () =>
    HttpResponse.json({ message: 'All todos deleted' })
  ),

  // DELETE /api/v1/session/:sessionId
  http.delete(`${API_BASE_URL}/session/:sessionId`, () =>
    HttpResponse.json({ message: 'Session deleted' })
  ),

  // POST /api/v1/session/:sessionId/instruction
  http.post<{ sessionId: string }, { instruction: string }, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/instruction`,
    () => HttpResponse.json({ message: 'Instruction sent successfully' })
  ),

  // POST /api/v1/session/:sessionId/stop
  http.post<{ sessionId: string }, never, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/stop`,
    () => HttpResponse.json({ message: 'Session stopped' })
  )
]

/**
 * MSW handlers for /session endpoints with error responses
 */
export const sessionErrorHandlers = [
  // GET /api/v1/session/:sessionId (error response)
  http.get(
    `${API_BASE_URL}/session/:sessionId`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to get session' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // DELETE /api/v1/session/:sessionId (error response)
  http.delete(
    `${API_BASE_URL}/session/:sessionId`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to delete session' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // PATCH /api/v1/session/:sessionId/meta (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/meta`,
    () => new HttpResponse(null, { status: 500 })
  ),

  // PATCH /api/v1/session/:sessionId/multi_step_reasoning (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/multi_step_reasoning`,
    () =>
      new HttpResponse(
        JSON.stringify({ message: 'Failed to update multi-step reasoning' }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      )
  ),

  // POST /api/v1/session/:sessionId/instruction (error response)
  http.post(
    `${API_BASE_URL}/session/:sessionId/instruction`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to send instruction.' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/session/:sessionId/stop (error response)
  http.post(
    `${API_BASE_URL}/session/:sessionId/stop`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to stop session' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
