import { useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  setLocalMultiStepEnabled: React.Dispatch<React.SetStateAction<boolean>>
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  sessionDetail,
  setLocalMultiStepEnabled
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
      setLocalMultiStepEnabled(checked)

      await updateMultiStepReasoning(currentSessionId, {
        multi_step_reasoning_enabled: checked
      })
    },
    [
      currentSessionId,
      sessionDetail,
      updateMultiStepReasoning,
      setLocalMultiStepEnabled
    ]
  )

  return { handleMultiStepReasoningChange }
}
