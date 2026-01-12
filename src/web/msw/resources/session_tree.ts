import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

/**
 * MSW handlers for /session_tree endpoints
 */
export const sessionTreeHandlers = [
  // GET /api/v1/session_tree
  http.get<
    never,
    never,
    { sessions: [string, SessionOverview][]; sessionTree?: SessionOverview[] }
  >(`${API_BASE_URL}/session_tree`, () => {
    const mockSessions: [string, SessionOverview][] = [
      [
        'test-session',
        {
          sessionId: 'test-session',
          purpose: 'Test Purpose',
          background: 'Test Background',
          lastUpdatedAt: '2024-01-01T00:00:00Z',
          multiStepReasoningEnabled: false,
          procedure: 'Test Procedure',
          roles: [],
          artifacts: [],
          tokenCount: 0
        }
      ]
    ]

    return HttpResponse.json({
      sessions: mockSessions
    })
  })
]

/**
 * MSW handlers for /session_tree endpoints with error responses
 */
export const sessionTreeErrorHandlers = [
  // GET /api/v1/session_tree (error response)
  http.get(
    `${API_BASE_URL}/session_tree`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to get session tree' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
