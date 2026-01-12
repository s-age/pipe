import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import type { EditSessionMetaRequest } from '@/lib/api/meta/editSessionMeta'
import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useSessionMetaActions } from '../useSessionMetaActions'

const server = setupServer(...sessionHandlers)

describe('useSessionMetaActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('handleMetaSave', () => {
    const mockId = 'test-session-id'
    const mockMeta: EditSessionMetaRequest = {
      purpose: 'Updated Purpose',
      background: 'Updated Background'
    }

    it('should save session metadata successfully and show success toast', async () => {
      const { result } = renderHook(() => useSessionMetaActions())

      await result.current.handleMetaSave(mockId, mockMeta)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Session metadata saved')
      })
    })

    it('should handle save error, show failure toast, and rethrow error', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useSessionMetaActions())

      await expect(result.current.handleMetaSave(mockId, mockMeta)).rejects.toThrow()

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        // The error message comes from the catch block: (error as Error).message || 'Failed to save session meta.'
        // In sessionErrorHandlers, it returns null body with 500 status for meta patch.
        // The client likely throws an error with a message.
      })
    })
  })

  describe('hook structure', () => {
    it('should return handleMetaSave function', () => {
      const { result } = renderHook(() => useSessionMetaActions())

      expect(result.current).toHaveProperty('handleMetaSave')
      expect(typeof result.current.handleMetaSave).toBe('function')
    })
  })
})
