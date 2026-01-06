import { useCallback } from 'react'
import { useParams } from 'react-router-dom'

import type { State, Actions } from '@/stores/useChatHistoryStore'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useChatHistoryPageLifecycle } from './useChatHistoryPageLifecycle'

type UseChatHistoryPageHandlersReturn = {
  expertMode: boolean
  refreshSessionsInStore: Actions['refreshSessions']
  sessionDetail: State['sessionDetail']
  sessions: State['sessionTree']['sessions']
  setSessionDetail: Actions['setSessionDetail']
  handleSelectSession: (sessionId: string) => Promise<void>
  onRefresh: (sessionId?: string) => Promise<void>
}

export const useChatHistoryPageHandlers = (): UseChatHistoryPageHandlersReturn => {
  const { '*': urlSessionId } = useParams<{ '*': string }>()
  const { actions, state } = useSessionStore()
  const {
    sessionDetail,
    sessionTree: { sessions },
    settings
  } = state

  const { refreshSessions, selectSession, setSessionDetail } = actions

  // Use URL session ID if available, otherwise fall back to store's currentSessionId
  const activeSessionId = urlSessionId as string

  const { fetchChatHistory } = useChatHistoryPageActions({
    currentSessionId: activeSessionId
  })

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
