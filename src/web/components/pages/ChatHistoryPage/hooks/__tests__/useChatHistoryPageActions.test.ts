import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import { bffHandlers, bffErrorHandlers } from '@/msw/resources/bff'
import { clearToasts, getToasts } from '@/stores/useToastStore'
import type { SessionPair } from '@/types/session'

import { useChatHistoryPageActions } from '../useChatHistoryPageActions'

const server = setupServer(...bffHandlers)

describe('useChatHistoryPageActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('fetchChatHistory', () => {
    it('should fetch chat history successfully with hierarchical tree', async () => {
      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory()

      expect(data).toBeDefined()
      expect(data?.sessionDetail).toBeDefined()
      expect(data?.sessionDetail?.sessionId).toBe('test-session-id')
      expect(Array.isArray(data?.sessions)).toBe(true)
      expect(data?.sessions).toHaveLength(1)
      // Verify it's a tree node (has children)
      expect((data?.sessions?.[0] as SessionTreeNode).children).toBeDefined()
    })

    it('should normalize legacy flat pairs to flat SessionOverview array', async () => {
      const mockLegacyPairs: SessionPair[] = [
        [
          'session-1',
          {
            sessionId: 'session-1',
            artifacts: [],
            background: '',
            lastUpdatedAt: new Date().toISOString(),
            multiStepReasoningEnabled: false,
            procedure: '',
            purpose: 'session 1 purpose',
            roles: [],
            tokenCount: 0
          }
        ]
      ]

      server.use(
        http.get(`${API_BASE_URL}/bff/chat_history`, () =>
          HttpResponse.json({
            data: {
              sessions: [],
              sessionTree: mockLegacyPairs,
              settings: {},
              currentSession: { sessionId: 'test-session-id' }
            }
          })
        )
      )

      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory()

      expect(data?.sessions).toHaveLength(1)
      expect(data?.sessions?.[0]).toHaveProperty('sessionId', 'session-1')
      expect(data?.sessions?.[0]).toHaveProperty('purpose', 'session 1 purpose')
    })

    it('should handle empty session tree', async () => {
      server.use(
        http.get(`${API_BASE_URL}/bff/chat_history`, () =>
          HttpResponse.json({
            data: {
              sessions: [],
              sessionTree: [],
              settings: {},
              currentSession: { sessionId: 'test-session-id' }
            }
          })
        )
      )

      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory()

      expect(data?.sessionDetail).toBeDefined()
      expect(data?.sessions).toBeUndefined()
    })

    it('should use provided sessionId instead of currentSessionId', async () => {
      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'default-id' })
      )

      const data = await result.current.fetchChatHistory('override-id')

      expect(data?.sessionDetail?.sessionId).toBe('override-id')
    })

    it('should handle API error and show failure toast', async () => {
      server.use(...bffErrorHandlers)

      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory()

      expect(data).toBeUndefined()
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to refresh sessions')
      })
    })
  })

  describe('hook structure', () => {
    it('should return fetchChatHistory function', () => {
      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: null })
      )

      expect(result.current).toHaveProperty('fetchChatHistory')
      expect(typeof result.current.fetchChatHistory).toBe('function')
    })
  })
})
