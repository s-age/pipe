import { useCallback } from 'react'

import { archiveSessions } from '@/lib/api/session_management/archiveSessions'
import { deleteArchivedSessions } from '@/lib/api/session_management/deleteArchivedSessions'
import { getArchivedSessions } from '@/lib/api/session_management/getArchivedSessions'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { useSessionStore } from '@/stores/useChatHistoryStore'
import { useToastStore } from '@/stores/useToastStore'

type Properties = {
  storeActions: ReturnType<typeof useSessionStore>['actions']
}

export const useSessionManagementActions = ({
  storeActions
}: Properties): {
  archiveSessions: (sessionIds: string[]) => Promise<void>
  deleteArchivedSessions: (parameters: {
    sessionIds?: string[]
    filePaths?: string[]
  }) => Promise<void>
} => {
  const { addToast } = useToastStore()

  const archiveSessionsAction = useCallback<(sessionIds: string[]) => Promise<void>>(
    async (sessionIds: string[]): Promise<void> => {
      try {
        const result = await archiveSessions({ sessionIds: sessionIds })
        addToast({
          status: 'success',
          title: `Archived ${result.archivedCount} out of ${result.totalRequested} session(s) successfully.`
        })
        // Refresh sessions after archiving
        const sessionTree = await getSessionTree()
        const sessions =
          sessionTree.sessionTree ||
          sessionTree.sessions.map(([_, overview]) => overview)
        storeActions.setSessions(sessions)
        // Refresh archived sessions
        const archivedSessions = await getArchivedSessions()
        storeActions.setArchivedSessions(archivedSessions)
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to archive sessions.'
        })
      }
    },
    [addToast, storeActions]
  )

  const deleteArchivedSessionsAction = useCallback<
    (parameters: { sessionIds?: string[]; filePaths?: string[] }) => Promise<void>
  >(
    async (parameters: {
      sessionIds?: string[]
      filePaths?: string[]
    }): Promise<void> => {
      try {
        const result = await deleteArchivedSessions(parameters)
        addToast({
          status: 'success',
          title: `Deleted ${result.deletedCount} out of ${result.totalRequested} archived session(s) successfully.`
        })
        // Refresh archived sessions after deletion
        const archivedSessions = await getArchivedSessions()
        storeActions.setArchivedSessions(archivedSessions)
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to delete archived sessions.'
        })
      }
    },
    [addToast, storeActions]
  )

  return {
    archiveSessions: archiveSessionsAction,
    deleteArchivedSessions: deleteArchivedSessionsAction
  }
}
