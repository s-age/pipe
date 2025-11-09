import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editMultiStepReasoning } from '@/lib/api/session/editMultiStepReasoning'
import type { EditMultiStepReasoningRequest } from '@/lib/api/session/editMultiStepReasoning'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useMultiStepReasoningActions = (): {
  updateMultiStepReasoning: (
    sessionId: string,
    payload: EditMultiStepReasoningRequest,
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const toast = useToast()

  const updateMultiStepReasoning = useCallback(
    async (sessionId: string, payload: EditMultiStepReasoningRequest) => {
      try {
        const result = await editMultiStepReasoning(sessionId, payload)
        toast.success(result?.message || 'Multi-step reasoning updated')

        return result
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update multi-step reasoning',
        )
        throw error
      }
    },
    [toast],
  )

  return { updateMultiStepReasoning }
}
