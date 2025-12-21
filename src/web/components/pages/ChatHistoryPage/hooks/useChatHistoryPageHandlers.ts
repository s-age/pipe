import { useCallback } from 'react'

import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useChatHistoryPageLifecycle } from './useChatHistoryPageLifecycle'

type UseChatHistoryPageHandlersReturn = {
  sessions: State['sessionTree']['sessions']
  sessionDetail: State['sessionDetail']
  expertMode: boolean
  handleSelectSession: (sessionId: string) => Promise<void>
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

  const handleSelectSession = useCallback(
    async (sessionId: string): Promise<void> => {
      // Update the current session ID in the store
      selectSession(sessionId, null)

      // Refresh to fetch the latest session metadata
      await onRefresh(sessionId)
    },
    [selectSession, onRefresh]
  )

  useChatHistoryPageLifecycle({ state, actions })

  const expertMode = (settings.expertMode as boolean) ?? true

  return {
    sessions,
    sessionDetail,
    expertMode,
    handleSelectSession,
    setSessionDetail,
    onRefresh,
    refreshSessionsInStore: refreshSessions
  }
}
