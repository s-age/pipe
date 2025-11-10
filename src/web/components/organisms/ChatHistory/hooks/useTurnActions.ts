import { useCallback } from 'react'

import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { editTurn } from '@/lib/api/session/editTurn'
import { forkSession } from '@/lib/api/session/forkSession'

export const useTurnActions = (
  onRefresh: () => Promise<void>
): {
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    newContent: string
  ) => Promise<void>
} => {
  const deleteTurnAction = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      await deleteTurn(sessionId, turnIndex)
      await onRefresh()
    },
    [onRefresh]
  )

  const forkSessionAction = useCallback(
    async (sessionId: string, forkIndex: number): Promise<void> => {
      await forkSession(sessionId, forkIndex)
      await onRefresh()
    },
    [onRefresh]
  )

  const editTurnAction = useCallback(
    async (sessionId: string, turnIndex: number, newContent: string): Promise<void> => {
      await editTurn(sessionId, turnIndex, { content: newContent })
      await onRefresh()
    },
    [onRefresh]
  )

  return {
    deleteTurnAction,
    forkSessionAction,
    editTurnAction
  }
}
