import { useCallback } from 'react'

import { sendInstruction } from '@/lib/api/session/sendInstruction'
import { emitToast } from '@/lib/toastEvents'

export type UseInstructionFormActionsReturn = {
  sendInstructionAction: (
    sessionId: string,
    instruction: string
  ) => Promise<{ message: string }>
}

export const useInstructionFormActions = (): UseInstructionFormActionsReturn => {
  const sendInstructionAction = useCallback(
    async (sessionId: string, instruction: string): Promise<{ message: string }> => {
      if (!sessionId) {
        emitToast.failure('Session ID is missing.')
        throw new Error('Session ID is missing.')
      }
      try {
        const result = await sendInstruction(sessionId, instruction)
        emitToast.success('Instruction sent successfully')

        return result
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to send instruction.')
        throw error
      }
    },
    []
  )

  return { sendInstructionAction }
}
