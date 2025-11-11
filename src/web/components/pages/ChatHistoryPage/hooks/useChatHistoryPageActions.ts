import { useCallback } from 'react'

import { getSessionDashboard } from '@/lib/api/bff/getSessionDashboard'
import type { Actions } from '@/stores/useChatHistoryStore'

type UseChatHistoryPageActionsProperties = {
  currentSessionId: string | null
  refreshSessions: Actions['refreshSessions']
}

export const useChatHistoryPageActions = ({
  currentSessionId,
  refreshSessions
}: UseChatHistoryPageActionsProperties): {
  onRefresh: () => Promise<void>
} => {
  const onRefresh = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      const dashBoard = await getSessionDashboard(currentSessionId)
      refreshSessions(
        dashBoard.current_session,
        dashBoard.session_tree.map(([id, session]) => ({
          ...session,
          session_id: id
        }))
      )
    }
  }, [currentSessionId, refreshSessions])

  return { onRefresh }
}
