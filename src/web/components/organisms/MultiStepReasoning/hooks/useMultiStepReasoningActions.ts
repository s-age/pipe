import { useCallback } from 'react'

import { editMultiStepReasoning } from '@/lib/api/session/editMultiStepReasoning'
import type { EditMultiStepReasoningRequest } from '@/lib/api/session/editMultiStepReasoning'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useMultiStepReasoningActions = (): {
  updateMultiStepReasoning: (
    sessionId: string,
    payload: EditMultiStepReasoningRequest
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const updateMultiStepReasoning = useCallback(
    async (sessionId: string, payload: EditMultiStepReasoningRequest) => {
      const result = await editMultiStepReasoning(sessionId, payload)

      return result
    },
    []
  )

  return { updateMultiStepReasoning }
}
