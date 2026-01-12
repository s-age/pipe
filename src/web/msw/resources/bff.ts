import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { ChatHistoryResponse } from '@/lib/api/bff/getChatHistory'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import type { Settings } from '@/types/settings'

const mockSettings: Settings = {
  apiMode: 'test',
  contextLimit: 1000,
  expertMode: false,
  hyperparameters: {
    temperature: 0.7,
    topP: 1,
    topK: 50
  },
  language: 'en',
  maxToolCalls: 10,
  model: 'test-model',
  referenceTtl: 3600,
  searchModel: 'test-search-model',
  sessionsPath: '/tmp',
  timezone: 'UTC',
  toolResponseExpiration: 3600,
  yolo: false
}

const createMockSession = (sessionId: string): SessionDetail => ({
  sessionId,
  artifacts: [],
  background: 'test background',
  hyperparameters: null,
  instruction: 'test instruction',
  multiStepReasoningEnabled: false,
  parent: null,
  procedure: null,
  purpose: 'test purpose',
  references: [],
  roles: [],
  todos: [],
  turns: []
})

const mockSessionTree: SessionTreeNode[] = [
  {
    sessionId: 'node-1',
    children: [],
    overview: {
      sessionId: 'node-1',
      artifacts: [],
      background: '',
      lastUpdatedAt: new Date().toISOString(),
      multiStepReasoningEnabled: false,
      procedure: '',
      purpose: 'node 1 purpose',
      roles: [],
      tokenCount: 0
    }
  }
]

/**
 * MSW handlers for /bff endpoints
 */
export const bffHandlers = [
  // GET /api/v1/bff/chat_history
  http.get<never, never, { data: ChatHistoryResponse }>(
    `${API_BASE_URL}/bff/chat_history`,
    ({ request }) => {
      const url = new URL(request.url)
      const sessionId = url.searchParams.get('sessionId') || 'test-session-id'

      return HttpResponse.json({
        data: {
          sessions: [],
          sessionTree: mockSessionTree,
          settings: mockSettings,
          currentSession: createMockSession(sessionId)
        }
      })
    }
  )
]

/**
 * MSW handlers for /bff endpoints with error responses
 */
export const bffErrorHandlers = [
  // GET /api/v1/bff/chat_history (error response)
  http.get(`${API_BASE_URL}/bff/chat_history`, () =>
    HttpResponse.json(
      { message: 'Failed to refresh sessions' },
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  )
]
