import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { metaHandlers, metaErrorHandlers } from '@/msw/resources/meta'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useReferenceActions } from '../useReferenceActions'

const server = setupServer(...metaHandlers)

describe('useReferenceActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useReferenceActions())

      expect(result.current).toHaveProperty('handleUpdateReferencePersist')
      expect(result.current).toHaveProperty('handleUpdateReferenceTtl')
      expect(result.current).toHaveProperty('handleToggleReferenceDisabled')
      expect(typeof result.current.handleUpdateReferencePersist).toBe('function')
      expect(typeof result.current.handleUpdateReferenceTtl).toBe('function')
      expect(typeof result.current.handleToggleReferenceDisabled).toBe('function')
    })
  })

  describe('handleUpdateReferencePersist', () => {
    it('should update reference persist state successfully and show success toast', async () => {
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleUpdateReferencePersist('test-session', 0, true)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Reference persist state updated successfully')
      })
    })

    it('should handle update reference persist error and show failure toast', async () => {
      server.use(...metaErrorHandlers)
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleUpdateReferencePersist('test-session', 0, true)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update reference persist state.')
      })
    })
  })

  describe('handleUpdateReferenceTtl', () => {
    it('should update reference TTL successfully and show success toast', async () => {
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleUpdateReferenceTtl('test-session', 0, 3600)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Reference TTL updated successfully')
      })
    })

    it('should handle update reference TTL error and show failure toast', async () => {
      server.use(...metaErrorHandlers)
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleUpdateReferenceTtl('test-session', 0, 3600)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update reference TTL.')
      })
    })
  })

  describe('handleToggleReferenceDisabled', () => {
    it('should toggle reference disabled state successfully and show success toast', async () => {
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleToggleReferenceDisabled('test-session', 0)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Reference disabled state updated successfully')
      })
    })

    it('should handle toggle reference disabled error and show failure toast', async () => {
      server.use(...metaErrorHandlers)
      const { result } = renderHook(() => useReferenceActions())

      await result.current.handleToggleReferenceDisabled('test-session', 0)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to update reference disabled state.')
      })
    })
  })
})
