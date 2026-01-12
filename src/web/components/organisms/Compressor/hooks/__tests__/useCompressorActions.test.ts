import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import type { CreateCompressorRequest } from '@/lib/api/session/compress'
import { compressHandlers, compressErrorHandlers } from '@/msw/resources/compress'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useCompressorActions } from '../useCompressorActions'

const server = setupServer(...compressHandlers)

describe('useCompressorActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('executeCompression', () => {
    const mockRequest: CreateCompressorRequest = {
      sessionId: 'test-session-id',
      startTurn: 1,
      endTurn: 5,
      policy: 'test-policy',
      targetLength: 100
    }

    it('should execute compression successfully and show success toast', async () => {
      const { result } = renderHook(() => useCompressorActions())

      const response = await result.current.executeCompression(mockRequest)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Compression started successfully')
      })

      expect(response).toEqual({
        message: 'Compression started successfully',
        sessionId: 'test-compressor-session-id',
        summary: 'Test summary'
      })
    })

    it('should handle execute compression error and show failure toast', async () => {
      server.use(...compressErrorHandlers)
      const { result } = renderHook(() => useCompressorActions())

      const response = await result.current.executeCompression(mockRequest)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to start compression')
      })

      expect(response).toBeUndefined()
    })
  })

  describe('approveCompression', () => {
    it('should approve compression successfully and show success toast', async () => {
      const { result } = renderHook(() => useCompressorActions())

      await result.current.approveCompression('compressor-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Compression approved successfully')
      })
    })

    it('should handle approve compression error and show failure toast', async () => {
      server.use(...compressErrorHandlers)
      const { result } = renderHook(() => useCompressorActions())

      await result.current.approveCompression('compressor-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to approve compression')
      })
    })
  })

  describe('denyCompression', () => {
    it('should deny compression successfully and show success toast', async () => {
      const { result } = renderHook(() => useCompressorActions())

      await result.current.denyCompression('compressor-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Compression denied successfully')
      })
    })

    it('should handle deny compression error and show failure toast', async () => {
      server.use(...compressErrorHandlers)
      const { result } = renderHook(() => useCompressorActions())

      await result.current.denyCompression('compressor-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to deny compression')
      })
    })
  })

  describe('return value structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useCompressorActions())

      expect(result.current).toHaveProperty('executeCompression')
      expect(result.current).toHaveProperty('approveCompression')
      expect(result.current).toHaveProperty('denyCompression')
      expect(typeof result.current.executeCompression).toBe('function')
      expect(typeof result.current.approveCompression).toBe('function')
      expect(typeof result.current.denyCompression).toBe('function')
    })
  })
})
