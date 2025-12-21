import { useCallback } from 'react'

import { useMultiStepReasoningActions } from '@/components/organisms/MultiStepReasoning/hooks/useMultiStepReasoningActions'
import type { SessionDetail } from '@/lib/api/session/getSession'

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

      // Intentionally not awaiting - errors are handled in Actions layer
      void updateMultiStepReasoning(currentSessionId, {
        multiStepReasoningEnabled: checked
      })
    },
    [currentSessionId, sessionDetail, updateMultiStepReasoning]
  )

  return { handleMultiStepReasoningChange }
}
