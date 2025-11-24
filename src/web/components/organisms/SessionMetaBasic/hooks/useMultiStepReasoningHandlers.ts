import { useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  sessionDetail
}: UseMultiStepReasoningHandlersProperties): {
  handleMultiStepReasoningChange: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => Promise<void>
} => {
  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleMultiStepReasoningChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      if (!currentSessionId || !sessionDetail) return

      const checked = event.target.checked

      void updateMultiStepReasoning(currentSessionId, {
        multi_step_reasoning_enabled: checked
      })
    },
    [currentSessionId, sessionDetail, updateMultiStepReasoning]
  )

  return { handleMultiStepReasoningChange }
}
