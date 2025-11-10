import { useCallback } from 'react'

import { getSessionDashboard } from '@/lib/api/bff/getSessionDashboard'
import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionLoader } from './useSessionLoader'

type UseChatHistoryPageLogicReturn = {
  sessions: State['sessionTree']['sessions']
  currentSessionId: State['sessionTree']['currentSessionId']
  sessionDetail: State['sessionDetail']
  expertMode: boolean
  selectSession: Actions['selectSession']
  setSessionDetail: Actions['setSessionDetail']
  onRefresh: () => Promise<void>
}

export const useChatHistoryPageLogic = (): UseChatHistoryPageLogicReturn => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail
  } = state

  const { selectSession, setSessionDetail, refreshSessions } = actions

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

  useSessionLoader({ state, actions })

  const expertMode = (state.settings.expertMode as boolean) ?? true

  return {
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh
  }
}
