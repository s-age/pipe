import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import {
  sessionManagementHandlers,
  sessionManagementErrorHandlers
} from '@/msw/resources/session_management'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useSessionManagementActions } from '../useSessionManagementActions'

const server = setupServer(...sessionManagementHandlers)

describe('useSessionManagementActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useSessionManagementActions())

      expect(result.current).toHaveProperty('archiveSessionsAction')
      expect(result.current).toHaveProperty('deleteArchivedSessionsAction')
      expect(typeof result.current.archiveSessionsAction).toBe('function')
      expect(typeof result.current.deleteArchivedSessionsAction).toBe('function')
    })
  })

  describe('archiveSessionsAction', () => {
    it('should archive sessions successfully and show success toast', async () => {
      const { result } = renderHook(() => useSessionManagementActions())
      const sessionIds = ['session-1', 'session-2']

      const success = await result.current.archiveSessionsAction(sessionIds)

      expect(success).toBe(true)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Archived 2 out of 2 session(s) successfully.')
      })
    })

    it('should handle archive error and show failure toast', async () => {
      server.use(...sessionManagementErrorHandlers)
      const { result } = renderHook(() => useSessionManagementActions())
      const sessionIds = ['session-1']

      const success = await result.current.archiveSessionsAction(sessionIds)

      expect(success).toBe(false)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to archive sessions.')
      })
    })
  })

  describe('deleteArchivedSessionsAction', () => {
    it('should delete archived sessions successfully and show success toast', async () => {
      const { result } = renderHook(() => useSessionManagementActions())
      const parameters = { sessionIds: ['session-1'], filePaths: ['path/1'] }

      const success = await result.current.deleteArchivedSessionsAction(parameters)

      expect(success).toBe(true)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe(
          'Deleted 2 out of 2 archived session(s) successfully.'
        )
      })
    })

    it('should handle delete error and show failure toast', async () => {
      server.use(...sessionManagementErrorHandlers)
      const { result } = renderHook(() => useSessionManagementActions())
      const parameters = { sessionIds: ['session-1'] }

      const success = await result.current.deleteArchivedSessionsAction(parameters)

      expect(success).toBe(false)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to delete archived sessions.')
      })
    })

    it('should work with empty parameters', async () => {
      const { result } = renderHook(() => useSessionManagementActions())

      const success = await result.current.deleteArchivedSessionsAction({})

      expect(success).toBe(true)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
      })
    })
  })
})
