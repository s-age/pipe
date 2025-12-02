import { useCallback } from 'react'

import { deleteSessions } from '@/lib/api/session/deleteSessions'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { useSessionStore } from '@/stores/useChatHistoryStore'
import { useToastStore } from '@/stores/useToastStore'

type Properties = {
  storeActions: ReturnType<typeof useSessionStore>['actions']
}

export const useSessionManagementActions = ({
  storeActions
}: Properties): {
  deleteSessions: (sessionIds: string[]) => Promise<void>
} => {
  const { addToast } = useToastStore()

  const deleteSessionsAction = useCallback<(sessionIds: string[]) => Promise<void>>(
    async (sessionIds: string[]): Promise<void> => {
      try {
        const result = await deleteSessions({ session_ids: sessionIds })
        addToast({
          status: 'success',
          title: `Deleted ${result.deleted_count} out of ${result.total_requested} session(s) successfully.`
        })
        // Refresh sessions after deletion
        const sessionTree = await getSessionTree()
        const sessions =
          sessionTree.session_tree ||
          sessionTree.sessions.map(([_, overview]) => overview)
        storeActions.setSessions(sessions)
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to delete sessions.'
        })
      }
    },
    [addToast, storeActions]
  )

  return {
    deleteSessions: deleteSessionsAction
  }
}
