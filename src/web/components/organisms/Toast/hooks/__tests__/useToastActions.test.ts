import { renderHook, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import { useAppStore } from '@/stores/useAppStore'
import { clearToasts, getToasts, addToast } from '@/stores/useToastStore'

import { useToastActions } from '../useToastActions'

// Mock useAppStore to redirect pushToast to useToastStore's addToast
// This allows us to use the standard verification pattern (getToasts)
// while respecting the requirement to not modify the target hook file.
vi.mock('@/stores/useAppStore', () => ({
  useAppStore: vi.fn()
}))

describe('useToastActions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    clearToasts()

    // Setup the mock to call addToast from useToastStore
    vi.mocked(useAppStore).mockReturnValue({
      pushToast: vi.fn((payload) => addToast(payload)),
      state: { toasts: [], loadingCount: 0 },
      clearToasts: vi.fn(),
      hideLoader: vi.fn(),
      removeToast: vi.fn(),
      showLoader: vi.fn(),
      isLoading: false
    } as unknown as ReturnType<typeof useAppStore>)
  })

  describe('show', () => {
    it('should show toast with provided parameters', async () => {
      const { result } = renderHook(() => useToastActions())
      const parameters = {
        status: 'success' as const,
        title: 'Test Title',
        description: 'Test Desc',
        duration: 3000,
        position: 'top-right' as const
      }

      const id = result.current.show(parameters)

      expect(id).toBeDefined()
      expect(typeof id).toBe('string')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Test Title')
        expect(toasts[0].description).toBe('Test Desc')
        expect(toasts[0].duration).toBe(3000)
        expect(toasts[0].position).toBe('top-right')
      })
    })
  })

  describe('success', () => {
    it('should show success toast with string title', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.success('Success Message')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Success Message')
      })
    })

    it('should show success toast with partial parameters', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.success({ title: 'Success Title', description: 'Success Desc' })

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Success Title')
        expect(toasts[0].description).toBe('Success Desc')
      })
    })
  })

  describe('failure', () => {
    it('should show failure toast with string title', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.failure('Error Message')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Error Message')
      })
    })

    it('should show failure toast with partial parameters', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.failure({ title: 'Error Title', description: 'Error Desc' })

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Error Title')
        expect(toasts[0].description).toBe('Error Desc')
      })
    })
  })

  describe('warning', () => {
    it('should show warning toast with string title', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.warning('Warning Message')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('warning')
        expect(toasts[0].title).toBe('Warning Message')
      })
    })

    it('should show warning toast with partial parameters', async () => {
      const { result } = renderHook(() => useToastActions())

      result.current.warning({ title: 'Warning Title', description: 'Warning Desc' })

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('warning')
        expect(toasts[0].title).toBe('Warning Title')
        expect(toasts[0].description).toBe('Warning Desc')
      })
    })
  })

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useToastActions())

      expect(result.current).toHaveProperty('show')
      expect(result.current).toHaveProperty('success')
      expect(result.current).toHaveProperty('failure')
      expect(result.current).toHaveProperty('warning')
      expect(typeof result.current.show).toBe('function')
      expect(typeof result.current.success).toBe('function')
      expect(typeof result.current.failure).toBe('function')
      expect(typeof result.current.warning).toBe('function')
    })
  })
})
