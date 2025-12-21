import { useCallback } from 'react'

import { archiveSessions } from '@/lib/api/session_management/archiveSessions'
import { deleteArchivedSessions } from '@/lib/api/session_management/deleteArchivedSessions'
import { useToastStore } from '@/stores/useToastStore'

export const useSessionManagementActions = (): {
  archiveSessionsAction: (sessionIds: string[]) => Promise<boolean>
  deleteArchivedSessionsAction: (parameters: {
    sessionIds?: string[]
    filePaths?: string[]
  }) => Promise<boolean>
} => {
  const { addToast } = useToastStore()

  const archiveSessionsAction = useCallback<(sessionIds: string[]) => Promise<boolean>>(
    async (sessionIds: string[]): Promise<boolean> => {
      try {
        const result = await archiveSessions({ sessionIds: sessionIds })
        addToast({
          status: 'success',
          title: `Archived ${result.archivedCount} out of ${result.totalRequested} session(s) successfully.`
        })

        return true
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to archive sessions.'
        })

        return false
      }
    },
    [addToast]
  )

  const deleteArchivedSessionsAction = useCallback<
    (parameters: { sessionIds?: string[]; filePaths?: string[] }) => Promise<boolean>
  >(
    async (parameters: {
      sessionIds?: string[]
      filePaths?: string[]
    }): Promise<boolean> => {
      try {
        const result = await deleteArchivedSessions(parameters)
        addToast({
          status: 'success',
          title: `Deleted ${result.deletedCount} out of ${result.totalRequested} archived session(s) successfully.`
        })

        return true
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to delete archived sessions.'
        })

        return false
      }
    },
    [addToast]
  )

  return {
    archiveSessionsAction,
    deleteArchivedSessionsAction
  }
}
