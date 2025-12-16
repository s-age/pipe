import { useCallback } from 'react'

import { sendInstruction } from '@/lib/api/session/sendInstruction'
import { addToast } from '@/stores/useToastStore'

export type UseInstructionFormActionsReturn = {
  sendInstructionAction: (
    sessionId: string,
    instruction: string
  ) => Promise<{ message: string } | void>
}

export const useInstructionFormActions = (): UseInstructionFormActionsReturn => {
  const sendInstructionAction = useCallback(
    async (sessionId: string, instruction: string): Promise<{ message: string } | void> => {
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

  return { sendInstructionAction }
}
