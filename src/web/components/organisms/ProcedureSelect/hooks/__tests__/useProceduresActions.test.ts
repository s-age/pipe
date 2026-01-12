import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { fsHandlers, fsErrorHandlers } from '@/msw/resources/fs'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useProceduresActions } from '../useProceduresActions'

const server = setupServer(...fsHandlers)

describe('useProceduresActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('hook structure', () => {
    it('should return fetchProcedures function', () => {
      const { result } = renderHook(() => useProceduresActions())

      expect(result.current).toHaveProperty('fetchProcedures')
      expect(typeof result.current.fetchProcedures).toBe('function')
    })
  })

  describe('fetchProcedures', () => {
    it('should fetch procedures successfully', async () => {
      const { result } = renderHook(() => useProceduresActions())

      const procedures = await result.current.fetchProcedures()

      expect(procedures).toEqual([
        { label: 'Procedure 1', value: 'proc-1' },
        { label: 'Procedure 2', value: 'proc-2' },
        { label: 'Procedure 3', value: 'proc-3' }
      ])

      const toasts = getToasts()
      expect(toasts).toHaveLength(0)
    })

    it('should handle fetch procedures error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useProceduresActions())

      const procedures = await result.current.fetchProcedures()

      expect(procedures).toBeUndefined()

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to fetch procedures')
      })
    })
  })
})
