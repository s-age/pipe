import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import {
  sessionTreeHandlers,
  sessionTreeErrorHandlers
} from '@/msw/resources/session_tree'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useChatHistoryActions } from '../useChatHistoryActions'

const server = setupServer(...sessionHandlers, ...sessionTreeHandlers)

describe('useChatHistoryActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('deleteSessionAction', () => {
    it('should delete session successfully and show success toast', async () => {
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      await result.current.deleteSessionAction('test-session')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Session deleted successfully')
      })
    })

    it('should handle delete session error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      await result.current.deleteSessionAction('test-session')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to delete session')
      })
    })
  })

  describe('refreshSession', () => {
    it('should return undefined if currentSessionId is null', async () => {
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: null })
      )

      const response = await result.current.refreshSession()

      expect(response).toBeUndefined()
      expect(getToasts()).toHaveLength(0)
    })

    it('should refresh session successfully and return session detail and overview', async () => {
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      const response = await result.current.refreshSession()

      await waitFor(() => {
        expect(response).toBeDefined()
        expect(response?.sessionDetail.sessionId).toBe('test-session')
        expect(response?.sessions).toHaveLength(1)
        expect(response?.sessions[0].sessionId).toBe('test-session')
      })
    })

    it('should handle refresh session error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      const response = await result.current.refreshSession()

      await waitFor(() => {
        expect(response).toBeUndefined()
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to get session')
      })
    })

    it('should handle session tree error and show failure toast', async () => {
      server.use(...sessionTreeErrorHandlers)
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      const response = await result.current.refreshSession()

      await waitFor(() => {
        expect(response).toBeUndefined()
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to get session tree')
      })
    })
  })

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() =>
        useChatHistoryActions({ currentSessionId: 'test-session' })
      )

      expect(result.current).toHaveProperty('deleteSessionAction')
      expect(result.current).toHaveProperty('refreshSession')
      expect(typeof result.current.deleteSessionAction).toBe('function')
      expect(typeof result.current.refreshSession).toBe('function')
    })
  })
})
