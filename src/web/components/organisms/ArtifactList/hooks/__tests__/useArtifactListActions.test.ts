import { renderHook } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { sessionHandlers, sessionErrorHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useArtifactListActions } from '../useArtifactListActions'

const server = setupServer(...sessionHandlers)

describe('useArtifactListActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('updateArtifacts', () => {
    it('should update artifacts successfully and show success toast', async () => {
      const { result } = renderHook(() => useArtifactListActions())

      await result.current.updateArtifacts('test-session-id', [
        'path/1.txt',
        'path/2.txt'
      ])

      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('success')
      expect(toasts[0].title).toBe('Artifacts updated successfully')
    })

    it('should handle update artifacts error and show failure toast', async () => {
      server.use(...sessionErrorHandlers)
      const { result } = renderHook(() => useArtifactListActions())

      await result.current.updateArtifacts('test-session-id', ['path/1.txt'])

      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('failure')
      expect(toasts[0].title).toContain('Failed to update artifacts')
    })
  })

  describe('hook structure', () => {
    it('should return updateArtifacts function', () => {
      const { result } = renderHook(() => useArtifactListActions())

      expect(result.current).toHaveProperty('updateArtifacts')
      expect(typeof result.current.updateArtifacts).toBe('function')
    })
  })
})
