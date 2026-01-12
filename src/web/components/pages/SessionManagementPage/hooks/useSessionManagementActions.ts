import { useCallback } from 'react'

import { archiveSessions } from '@/lib/api/session_management/archiveSessions'
import { deleteArchivedSessions } from '@/lib/api/session_management/deleteArchivedSessions'
import { addToast } from '@/stores/useToastStore'

export const useSessionManagementActions = (): {
  archiveSessionsAction: (sessionIds: string[]) => Promise<boolean>
  deleteArchivedSessionsAction: (parameters: {
    filePaths?: string[]
    sessionIds?: string[]
  }) => Promise<boolean>
} => {

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
    []
  )

  const deleteArchivedSessionsAction = useCallback<
    (parameters: { filePaths?: string[]; sessionIds?: string[] }) => Promise<boolean>
  >(
    async (parameters: {
      filePaths?: string[]
      sessionIds?: string[]
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
    []
  )

  return {
    archiveSessionsAction,
    deleteArchivedSessionsAction
  }
}
