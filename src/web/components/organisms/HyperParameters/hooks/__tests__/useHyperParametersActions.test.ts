import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { API_BASE_URL } from '@/constants/uri'
import { metaHandlers, metaErrorHandlers } from '@/msw/resources/meta'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useHyperParametersActions } from '../useHyperParametersActions'

const server = setupServer(...metaHandlers)

describe('useHyperParametersActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('updateHyperparameters', () => {
    it('should update hyperparameters successfully and show success toast', async () => {
      const { result } = renderHook(() => useHyperParametersActions())
      const sessionId = 'test-session-id'
      const payload = { temperature: 0.7, topP: 0.9, topK: 5 }

      const response = await result.current.updateHyperparameters(sessionId, payload)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Hyperparameters updated successfully')
      })

      expect(response).toBeDefined()
      if (response) {
        expect(response.message).toBe('Hyperparameters updated successfully')
        expect(response.session.sessionId).toBe(sessionId)
      }
    })

    it('should handle update error and show failure toast', async () => {
      server.use(...metaErrorHandlers)
      const { result } = renderHook(() => useHyperParametersActions())
      const sessionId = 'test-session-id'
      const payload = { temperature: 0.7 }

      const response = await result.current.updateHyperparameters(sessionId, payload)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update hyperparameters')
      })

      expect(response).toBeUndefined()
    })

    it('should use default success message if result.message is missing', async () => {
      server.use(
        http.patch(`${API_BASE_URL}/session/:sessionId/hyperparameters`, () =>
          HttpResponse.json({
            session: { sessionId: 'test-session-id' }
          })
        )
      )
      const { result } = renderHook(() => useHyperParametersActions())

      await result.current.updateHyperparameters('test-session-id', {
        temperature: 0.5
      })

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Hyperparameters updated')
      })
    })
  })

  describe('hook structure', () => {
    it('should return updateHyperparameters function', () => {
      const { result } = renderHook(() => useHyperParametersActions())
      expect(result.current).toHaveProperty('updateHyperparameters')
      expect(typeof result.current.updateHyperparameters).toBe('function')
    })
  })
})
