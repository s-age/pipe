import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { bffHandlers, bffErrorHandlers } from '@/msw/resources/bff'
import { clearToasts, getToasts } from '@/stores/useToastStore'

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
    it('should fetch chat history successfully', async () => {
      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory()

      expect(data).toBeDefined()
      expect(data?.sessionDetail?.sessionId).toBe('test-session-id')
      expect(data?.sessions).toBeDefined()
    })

    it('should fetch chat history with specific sessionId', async () => {
      const { result } = renderHook(() =>
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      const data = await result.current.fetchChatHistory('other-session-id')

      expect(data).toBeDefined()
      expect(data?.sessionDetail?.sessionId).toBe('other-session-id')
    })

    it('should handle fetch error and show failure toast', async () => {
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
        useChatHistoryPageActions({ currentSessionId: 'test-session-id' })
      )

      expect(result.current).toHaveProperty('fetchChatHistory')
      expect(typeof result.current.fetchChatHistory).toBe('function')
    })
  })
})
