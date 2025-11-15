import { useCallback } from 'react'

import { deleteSession } from '@/lib/api/session/deleteSession'
import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { editTurn } from '@/lib/api/session/editTurn'
import { forkSession } from '@/lib/api/session/forkSession'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail, Turn } from '@/lib/api/session/getSession'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

type UseChatHistoryActionsProperties = {
  currentSessionId: string | null
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

type UseChatHistoryActionsReturn = {
  deleteSessionAction: (sessionId: string) => Promise<void>
  refreshSession: () => Promise<void>
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (
    sessionId: string,
    forkIndex: number
  ) => Promise<{ new_session_id: string }>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    newContent: string,
    turn: Turn
  ) => Promise<void>
}

export const useChatHistoryActions = ({
  currentSessionId,
  refreshSessionsInStore
}: UseChatHistoryActionsProperties): UseChatHistoryActionsReturn => {
  // Session actions
  const deleteSessionAction = useCallback(async (sessionId: string): Promise<void> => {
    await deleteSession(sessionId)
  }, [])

  const refreshSession = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      const fetchedSessionDetailResponse = await getSession(currentSessionId)
      const fetchedSessionTree = await getSessionTree()
      const newSessions = fetchedSessionTree.sessions.map(([id, session]) => ({
        ...session,
        session_id: id
      }))
      refreshSessionsInStore(fetchedSessionDetailResponse.session, newSessions)
    }
  }, [currentSessionId, refreshSessionsInStore])

  // Turn actions
  const deleteTurnAction = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      await deleteTurn(sessionId, turnIndex)
      await refreshSession()
    },
    [refreshSession]
  )

  const forkSessionAction = useCallback(
    async (
      sessionId: string,
      forkIndex: number
    ): Promise<{ new_session_id: string }> => {
      const response = await forkSession(sessionId, forkIndex)

      return response
    },
    []
  )

  const editTurnAction = useCallback(
    async (
      sessionId: string,
      turnIndex: number,
      newContent: string,
      turn: Turn
    ): Promise<void> => {
      // Send the appropriate field based on turn type
      const updateData =
        turn.type === 'user_task'
          ? { instruction: newContent }
          : { content: newContent }

      await editTurn(sessionId, turnIndex, updateData)
      // Note: refreshSession is called by the handler after this succeeds
    },
    []
  )

  return {
    // Session actions
    deleteSessionAction,
    refreshSession,
    // Turn actions
    deleteTurnAction,
    forkSessionAction,
    editTurnAction
  }
}
