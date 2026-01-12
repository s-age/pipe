import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useInstructionFormActions } from '../useInstructionFormActions'

const server = setupServer(...sessionHandlers)

describe('useInstructionFormActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('sendInstructionAction', () => {
    it('should send instruction successfully and show success toast', async () => {
      const { result } = renderHook(() => useInstructionFormActions())

      const response = await result.current.sendInstructionAction(
        'test-session-id',
        'test instruction'
      )

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Instruction sent successfully')
      })
      expect(response).toEqual({ message: 'Instruction sent successfully' })
    })

    it('should show failure toast when sessionId is missing', async () => {
      const { result } = renderHook(() => useInstructionFormActions())

      await result.current.sendInstructionAction('', 'test instruction')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Session ID is missing.')
      })
    })

    it('should handle send instruction error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useInstructionFormActions())

      await result.current.sendInstructionAction('test-session-id', 'test instruction')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to send instruction.')
      })
    })
  })

  describe('stopSession', () => {
    it('should stop session successfully and show success toast', async () => {
      const { result } = renderHook(() => useInstructionFormActions())

      await result.current.stopSession('test-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Session stopped')
      })
    })

    it('should handle stop session error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useInstructionFormActions())

      await result.current.stopSession('test-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to stop session')
      })
    })
  })

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useInstructionFormActions())

      expect(result.current).toHaveProperty('sendInstructionAction')
      expect(result.current).toHaveProperty('stopSession')
      expect(typeof result.current.sendInstructionAction).toBe('function')
      expect(typeof result.current.stopSession).toBe('function')
    })
  })
})
