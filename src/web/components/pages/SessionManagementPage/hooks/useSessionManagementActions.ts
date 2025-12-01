import { useCallback } from 'react'

import { deleteSessions } from '@/lib/api/session/deleteSessions'
import { useToastStore } from '@/stores/useToastStore'

export const useSessionManagementActions = (): {
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
      } catch {
        addToast({
          status: 'failure',
          title: 'Failed to delete sessions.'
        })
      }
    },
    [addToast]
  )

  return {
    deleteSessions: deleteSessionsAction
  }
}
