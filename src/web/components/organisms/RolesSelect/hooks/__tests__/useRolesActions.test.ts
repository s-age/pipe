import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { fsHandlers, fsErrorHandlers } from '@/msw/resources/fs'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useRolesActions } from '../useRolesActions'

const server = setupServer(...fsHandlers)

describe('useRolesActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('fetchRoles', () => {
    it('should fetch roles successfully', async () => {
      const { result } = renderHook(() => useRolesActions())

      const roles = await result.current.fetchRoles()

      expect(roles).toEqual([
        { label: 'Admin', value: 'admin' },
        { label: 'Editor', value: 'editor' },
        { label: 'Viewer', value: 'viewer' }
      ])
      expect(getToasts()).toHaveLength(0)
    })

    it('should handle fetch roles error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useRolesActions())

      const roles = await result.current.fetchRoles()

      expect(roles).toBeUndefined()
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to fetch roles')
      })
    })
  })

  describe('hook structure', () => {
    it('should return fetchRoles function', () => {
      const { result } = renderHook(() => useRolesActions())

      expect(result.current).toHaveProperty('fetchRoles')
      expect(typeof result.current.fetchRoles).toBe('function')
    })
  })
})
