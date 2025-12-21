import { useCallback } from 'react'

import { editMultiStepReasoning } from '@/lib/api/meta/editMultiStepReasoning'
import type { EditMultiStepReasoningRequest } from '@/lib/api/meta/editMultiStepReasoning'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'

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
        addToast({
          status: 'success',
          title: result?.message || 'Multi-step reasoning updated'
        })

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update multi-step reasoning'
        })
      }
    },
    []
  )

  return { updateMultiStepReasoning }
}
