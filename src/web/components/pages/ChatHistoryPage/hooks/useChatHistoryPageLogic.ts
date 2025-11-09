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
  refreshSessions: Actions['refreshSessions']
  actions: Actions
}

export const useChatHistoryPageLogic = (): UseChatHistoryPageLogicReturn => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
  } = state

  const { selectSession, setSessionDetail, refreshSessions } = actions

  useSessionLoader({ state, actions })

  const expertMode = (state.settings.expertMode as boolean) ?? true

  return {
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    refreshSessions,
    actions,
  }
}
