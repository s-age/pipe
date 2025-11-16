import { useCallback } from 'react'

import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { editTurn } from '@/lib/api/session/editTurn'
import { forkSession } from '@/lib/api/session/forkSession'
import type { Turn } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

export type UseTurnActionsReturn = {
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    newContent: string,
    turn: Turn
  ) => Promise<void>
}

export const useTurnActions = (): UseTurnActionsReturn => {
  const deleteTurnAction = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      try {
        await deleteTurn(sessionId, turnIndex)
        emitToast.success('Turn deleted successfully')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to delete turn.')
        throw error
      }
    },
    []
  )

  const forkSessionAction = useCallback(
    async (sessionId: string, forkIndex: number): Promise<void> => {
      try {
        const response = await forkSession(sessionId, forkIndex)
        emitToast.success('Session forked successfully')
        window.location.href = `/session/${response.new_session_id}`
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to fork session.')
        throw error
      }
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
      try {
        // Send the appropriate field based on turn type
        const updateData =
          turn.type === 'user_task'
            ? { instruction: newContent }
            : { content: newContent }

        await editTurn(sessionId, turnIndex, updateData)
        emitToast.success('Turn updated successfully')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update turn.')
        throw error
      }
    },
    []
  )

  return {
    deleteTurnAction,
    forkSessionAction,
    editTurnAction
  }
}
