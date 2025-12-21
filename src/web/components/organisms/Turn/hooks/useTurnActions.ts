import { useCallback } from 'react'

import type { Turn } from '@/lib/api/session/getSession'
import { deleteTurn } from '@/lib/api/turn/deleteTurn'
import { editTurn } from '@/lib/api/turn/editTurn'
import { forkSession } from '@/lib/api/turn/forkSession'
import { addToast } from '@/stores/useToastStore'

export type UseTurnActionsReturn = {
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (
    sessionId: string,
    forkIndex: number
  ) => Promise<string | undefined>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    new_content: string,
    turn: Turn
  ) => Promise<void>
}

export const useTurnActions = (): UseTurnActionsReturn => {
  const deleteTurnAction = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      try {
        await deleteTurn(sessionId, turnIndex)
        addToast({ status: 'success', title: 'Turn deleted successfully' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to delete turn.'
        })
      }
    },
    []
  )

  const forkSessionAction = useCallback(
    async (sessionId: string, forkIndex: number): Promise<string | undefined> => {
      try {
        const response = await forkSession(sessionId, forkIndex)
        addToast({ status: 'success', title: 'Session forked successfully' })

        return response.newSessionId
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to fork session.'
        })

        return undefined
      }
    },
    []
  )

  const editTurnAction = useCallback(
    async (
      sessionId: string,
      turnIndex: number,
      new_content: string,
      turn: Turn
    ): Promise<void> => {
      try {
        // Send the appropriate field based on turn type
        const updateData =
          turn.type === 'user_task'
            ? { instruction: new_content }
            : { content: new_content }

        await editTurn(sessionId, turnIndex, updateData)
        addToast({ status: 'success', title: 'Turn updated successfully' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update turn.'
        })
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
