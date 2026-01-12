import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import type { Turn } from '@/lib/api/session/getSession'
import { turnHandlers, turnErrorHandlers } from '@/msw/resources/turn'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useTurnActions } from '../useTurnActions'

const server = setupServer(...turnHandlers)

describe('useTurnActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('deleteTurnAction', () => {
    it('should delete turn successfully and show success toast', async () => {
      const { result } = renderHook(() => useTurnActions())

      await result.current.deleteTurnAction('test-session-id', 1)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Turn deleted successfully')
      })
    })

    it('should handle delete turn error and show failure toast', async () => {
      server.use(...turnErrorHandlers)
      const { result } = renderHook(() => useTurnActions())

      await result.current.deleteTurnAction('test-session-id', 1)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to delete turn')
      })
    })
  })

  describe('forkSessionAction', () => {
    it('should fork session successfully and return new session ID', async () => {
      const { result } = renderHook(() => useTurnActions())

      const newSessionId = await result.current.forkSessionAction(
        'test-session-id',
        2
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Session forked successfully')
      })
      expect(newSessionId).toBe('forked-session-test-session-id')
    })

    it('should handle fork session error and return undefined', async () => {
      server.use(...turnErrorHandlers)
      const { result } = renderHook(() => useTurnActions())

      const newSessionId = await result.current.forkSessionAction(
        'test-session-id',
        2
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to fork session')
      })
      expect(newSessionId).toBeUndefined()
    })
  })

  describe('editTurnAction', () => {
    it('should edit user_task turn successfully with instruction field', async () => {
      const { result } = renderHook(() => useTurnActions())
      const userTaskTurn: Turn = {
        type: 'user_task',
        instruction: 'original instruction',
        timestamp: '2024-01-01T00:00:00Z'
      }

      await result.current.editTurnAction(
        'test-session-id',
        0,
        'updated instruction',
        userTaskTurn
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Turn updated successfully')
      })
    })

    it('should edit model_response turn successfully with content field', async () => {
      const { result } = renderHook(() => useTurnActions())
      const modelResponseTurn: Turn = {
        type: 'model_response',
        content: 'original content',
        timestamp: '2024-01-01T00:00:00Z'
      }

      await result.current.editTurnAction(
        'test-session-id',
        1,
        'updated content',
        modelResponseTurn
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Turn updated successfully')
      })
    })

    it('should handle edit turn error and show failure toast', async () => {
      server.use(...turnErrorHandlers)
      const { result } = renderHook(() => useTurnActions())
      const userTaskTurn: Turn = {
        type: 'user_task',
        instruction: 'original instruction',
        timestamp: '2024-01-01T00:00:00Z'
      }

      await result.current.editTurnAction(
        'test-session-id',
        0,
        'updated instruction',
        userTaskTurn
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update turn')
      })
    })
  })

  describe('return value structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useTurnActions())

      expect(result.current).toHaveProperty('deleteTurnAction')
      expect(result.current).toHaveProperty('editTurnAction')
      expect(result.current).toHaveProperty('forkSessionAction')
      expect(typeof result.current.deleteTurnAction).toBe('function')
      expect(typeof result.current.editTurnAction).toBe('function')
      expect(typeof result.current.forkSessionAction).toBe('function')
    })
  })
})
