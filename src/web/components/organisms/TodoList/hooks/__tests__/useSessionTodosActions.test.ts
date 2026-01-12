import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'
import type { Todo } from '@/types/todo'

import { useSessionTodosActions } from '../useSessionTodosActions'

const server = setupServer(...sessionHandlers)

describe('useSessionTodosActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useSessionTodosActions())

      expect(result.current).toHaveProperty('updateTodos')
      expect(result.current).toHaveProperty('deleteAllTodos')
      expect(typeof result.current.updateTodos).toBe('function')
      expect(typeof result.current.deleteAllTodos).toBe('function')
    })
  })

  describe('updateTodos', () => {
    const mockSessionId = 'test-session-id'
    const mockTodos: Todo[] = [{ title: 'Test Todo', checked: false }]

    it('should update todos successfully and show success toast', async () => {
      const { result } = renderHook(() => useSessionTodosActions())

      await result.current.updateTodos(mockSessionId, mockTodos)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Todos updated')
      })
    })

    it('should handle update todos error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useSessionTodosActions())

      await result.current.updateTodos(mockSessionId, mockTodos)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update todos')
      })
    })
  })

  describe('deleteAllTodos', () => {
    const mockSessionId = 'test-session-id'

    it('should delete all todos successfully and show success toast', async () => {
      const { result } = renderHook(() => useSessionTodosActions())

      await result.current.deleteAllTodos(mockSessionId)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('All todos deleted')
      })
    })

    it('should handle delete all todos error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useSessionTodosActions())

      await result.current.deleteAllTodos(mockSessionId)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to delete all todos')
      })
    })
  })
})
