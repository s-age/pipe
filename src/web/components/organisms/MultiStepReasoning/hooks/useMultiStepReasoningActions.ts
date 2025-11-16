import { useCallback } from 'react'

import { editMultiStepReasoning } from '@/lib/api/session/editMultiStepReasoning'
import type { EditMultiStepReasoningRequest } from '@/lib/api/session/editMultiStepReasoning'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

export const useMultiStepReasoningActions = (): {
  updateMultiStepReasoning: (
    sessionId: string,
    payload: EditMultiStepReasoningRequest
  ) => Promise<{ message: string; session: SessionDetail } | void>
} => {
  const updateMultiStepReasoning = useCallback(
    async (
      sessionId: string,
      payload: EditMultiStepReasoningRequest
    ): Promise<{ message: string; session: SessionDetail } | void> => {
      try {
        const result = await editMultiStepReasoning(sessionId, payload)
        emitToast.success(result?.message || 'Multi-step reasoning updated')

        return result
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update multi-step reasoning'
        )
      }
    },
    []
  )

  return { updateMultiStepReasoning }
}
