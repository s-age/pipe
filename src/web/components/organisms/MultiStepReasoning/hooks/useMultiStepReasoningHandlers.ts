import { useCallback } from 'react'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  multiStepReasoningEnabled: boolean
  setLocalEnabled: React.Dispatch<React.SetStateAction<boolean>>
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  multiStepReasoningEnabled,
  setLocalEnabled
}: UseMultiStepReasoningHandlersProperties): {
  handleMultiStepReasoningChange: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => Promise<void>
} => {
  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleMultiStepReasoningChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      if (!currentSessionId) return

      const checked = event.target.checked

      // Update local state for immediate UI feedback
      setLocalEnabled(checked)

      void updateMultiStepReasoning(currentSessionId, {
        multi_step_reasoning_enabled: checked
      })
      // On error, revert local state to the original value
      setLocalEnabled(multiStepReasoningEnabled)
    },
    [
      currentSessionId,
      multiStepReasoningEnabled,
      updateMultiStepReasoning,
      setLocalEnabled
    ]
  )

  return { handleMultiStepReasoningChange }
}
