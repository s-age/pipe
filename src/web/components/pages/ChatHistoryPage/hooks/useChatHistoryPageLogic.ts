import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionDetailLoader } from './useSessionDetailLoader'
import { useSessionLoader } from './useSessionLoader'

type UseChatHistoryPageLogicReturn = {
  errorMessage: string | null
  sessions: State['sessionTree']['sessions']
  currentSessionId: State['sessionTree']['currentSessionId']
  sessionDetail: State['sessionDetail']
  expertMode: boolean
  selectSession: Actions['selectSession']
  setSessionDetail: Actions['setSessionDetail']
  setError: Actions['setError']
  refreshSessions: Actions['refreshSessions']
  actions: Actions
}

export const useChatHistoryPageLogic = (): UseChatHistoryPageLogicReturn => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    error,
  } = state

  const { selectSession, setSessionDetail, setError, refreshSessions } = actions

  useSessionLoader({ state, actions })
  useSessionDetailLoader({ state, actions })

  const expertMode = (state.settings.expertMode as boolean) ?? true

  if (error) {
    return {
      errorMessage: error,
      sessions: [],
      currentSessionId: null,
      sessionDetail: null,
      expertMode: false,
      selectSession,
      setSessionDetail,
      setError,
      refreshSessions,
      actions,
    }
  }

  return {
    errorMessage: null,
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    setError,
    refreshSessions,
    actions,
  }
}
