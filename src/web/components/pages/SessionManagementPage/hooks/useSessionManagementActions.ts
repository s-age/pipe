import { useCallback } from 'react'

import { archiveSessions } from '@/lib/api/session/archiveSessions'
import { deleteArchivedSessions } from '@/lib/api/session/deleteArchivedSessions'
import { getArchivedSessions } from '@/lib/api/session/getArchivedSessions'
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
  deleteArchivedSessions: (sessionIds: string[]) => Promise<void>
} => {
  const { addToast } = useToastStore()

  const archiveSessionsAction = useCallback<(sessionIds: string[]) => Promise<void>>(
    async (sessionIds: string[]): Promise<void> => {
      try {
        const result = await archiveSessions({ session_ids: sessionIds })
        addToast({
          status: 'success',
          title: `Archived ${result.archived_count} out of ${result.total_requested} session(s) successfully.`
        })
        // Refresh sessions after archiving
        const sessionTree = await getSessionTree()
        const sessions =
          sessionTree.session_tree ||
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
    (sessionIds: string[]) => Promise<void>
  >(
    async (sessionIds: string[]): Promise<void> => {
      try {
        const result = await deleteArchivedSessions({ session_ids: sessionIds })
        addToast({
          status: 'success',
          title: `Deleted ${result.deleted_count} out of ${result.total_requested} archived session(s) successfully.`
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
