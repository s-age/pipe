import { useCallback } from 'react'

import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useChatHistoryPageLifecycle } from './useChatHistoryPageLifecycle'

type UseChatHistoryPageHandlersReturn = {
  sessions: State['sessionTree']['sessions']
  sessionDetail: State['sessionDetail']
  expertMode: boolean
  selectSession: Actions['selectSession']
  setSessionDetail: Actions['setSessionDetail']
  onRefresh: (sessionId?: string) => Promise<void>
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

  const { fetchChatHistory } = useChatHistoryPageActions({ currentSessionId })

  const onRefresh = useCallback(
    async (sessionId?: string): Promise<void> => {
      const result = await fetchChatHistory(sessionId)
      if (result) {
        refreshSessions(result.sessionDetail, result.sessions)
      }
    },
    [fetchChatHistory, refreshSessions]
  )

  useChatHistoryPageLifecycle({ state, actions })

  const expertMode = (settings.expertMode as boolean) ?? true

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
