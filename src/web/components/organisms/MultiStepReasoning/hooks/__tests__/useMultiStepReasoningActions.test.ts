import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useMultiStepReasoningActions } from '../useMultiStepReasoningActions'

const server = setupServer(...sessionHandlers)

describe('useMultiStepReasoningActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('updateMultiStepReasoning', () => {
    it('should update multi-step reasoning successfully and show success toast', async () => {
      const { result } = renderHook(() => useMultiStepReasoningActions())
      const sessionId = 'test-session-id'
      const payload = { multiStepReasoningEnabled: true }

      const response = await result.current.updateMultiStepReasoning(sessionId, payload)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Multi-step reasoning updated')
      })

      expect(response).toBeDefined()
      if (response) {
        expect(response.session.multiStepReasoningEnabled).toBe(true)
      }
    })

    it('should handle update error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useMultiStepReasoningActions())
      const sessionId = 'test-session-id'
      const payload = { multiStepReasoningEnabled: true }

      const response = await result.current.updateMultiStepReasoning(sessionId, payload)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update multi-step reasoning')
      })

      expect(response).toBeUndefined()
    })
  })

  describe('hook structure', () => {
    it('should return updateMultiStepReasoning function', () => {
      const { result } = renderHook(() => useMultiStepReasoningActions())

      expect(result.current).toHaveProperty('updateMultiStepReasoning')
      expect(typeof result.current.updateMultiStepReasoning).toBe('function')
    })
  })
})
