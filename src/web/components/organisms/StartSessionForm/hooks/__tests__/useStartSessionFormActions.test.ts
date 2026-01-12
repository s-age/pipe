import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { API_BASE_URL } from '@/constants/uri'
import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import type { StartSessionFormInputs } from '../../schema'
import { useStartSessionFormActions } from '../useStartSessionFormActions'

const server = setupServer(...sessionHandlers)

describe('useStartSessionFormActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  const mockInputs: StartSessionFormInputs = {
    sessionId: 'test-session-id',
    purpose: 'Test Purpose',
    background: 'Test Background',
    instruction: 'Test Instruction',
    artifacts: [],
    roles: [],
    references: [],
    hyperparameters: null,
    multiStepReasoningEnabled: false,
    parent: null,
    procedure: null,
    todos: [],
    turns: []
  }

  describe('startSessionAction', () => {
    it('should create session successfully and show success toast', async () => {
      const { result } = renderHook(() => useStartSessionFormActions())

      const actionResult = await result.current.startSessionAction(mockInputs)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Session created successfully')
      })

      expect(actionResult).toEqual({ sessionId: 'test-session-id' })
    })

    it('should handle API error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useStartSessionFormActions())

      const actionResult = await result.current.startSessionAction(mockInputs)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to create session')
      })

      expect(actionResult).toBeUndefined()
    })

    it('should handle unexpected response (missing sessionId) and show failure toast', async () => {
      server.use(
        http.post(`${API_BASE_URL}/session/start`, () =>
          HttpResponse.json({ sessionId: '' })
        )
      )

      const { result } = renderHook(() => useStartSessionFormActions())
      const actionResult = await result.current.startSessionAction(mockInputs)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe(
          'Failed to create session: No session ID returned.'
        )
      })

      expect(actionResult).toBeUndefined()
    })
  })

  describe('hook structure', () => {
    it('should return startSessionAction function', () => {
      const { result } = renderHook(() => useStartSessionFormActions())

      expect(result.current).toHaveProperty('startSessionAction')
      expect(typeof result.current.startSessionAction).toBe('function')
    })
  })
})
