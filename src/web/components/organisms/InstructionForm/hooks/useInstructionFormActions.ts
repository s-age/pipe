import { useCallback } from 'react'

import { sendInstruction } from '@/lib/api/session/sendInstruction'
import { stopSession as stopSessionApi } from '@/lib/api/session/stopSession'
import { addToast } from '@/stores/useToastStore'

export type UseInstructionFormActionsReturn = {
  sendInstructionAction: (
    sessionId: string,
    instruction: string
  ) => Promise<{ message: string } | void>
  stopSession: (sessionId: string) => Promise<void>
}

export const useInstructionFormActions = (): UseInstructionFormActionsReturn => {
  const sendInstructionAction = useCallback(
    async (
      sessionId: string,
      instruction: string
    ): Promise<{ message: string } | void> => {
      if (!sessionId) {
        addToast({ status: 'failure', title: 'Session ID is missing.' })

        return
      }
      try {
        const result = await sendInstruction(sessionId, instruction)
        addToast({ status: 'success', title: 'Instruction sent successfully' })

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to send instruction.'
        })
      }
    },
    []
  )

  const stopSession = useCallback(async (sessionId: string): Promise<void> => {
    try {
      await stopSessionApi(sessionId)
      addToast({
        status: 'success',
        title: 'Session stopped'
      })
    } catch (error) {
      addToast({
        status: 'failure',
        title: 'Failed to stop session',
        description: error instanceof Error ? error.message : undefined
      })
    }
  }, [])

  return { sendInstructionAction, stopSession }
}
