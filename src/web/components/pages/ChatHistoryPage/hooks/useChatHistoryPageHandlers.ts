import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useSessionLoader } from './useChatHistoryPageLifecycle'

type UseChatHistoryPageHandlersReturn = {
  sessions: State['sessionTree']['sessions']
  sessionDetail: State['sessionDetail']
  expertMode: boolean
  selectSession: Actions['selectSession']
  setSessionDetail: Actions['setSessionDetail']
  onRefresh: () => Promise<void>
  refreshSessionsInStore: Actions['refreshSessions']
}

export const useChatHistoryPageHandlers = (): UseChatHistoryPageHandlersReturn => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    settings
  } = state

  const { selectSession, setSessionDetail, refreshSessions } = actions

  const { onRefresh } = useChatHistoryPageActions({ currentSessionId, refreshSessions })

  useSessionLoader({ state, actions })

  const expertMode = (settings.expert_mode as boolean) ?? true

  return {
    sessions,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh,
    refreshSessionsInStore: refreshSessions
  }
}
