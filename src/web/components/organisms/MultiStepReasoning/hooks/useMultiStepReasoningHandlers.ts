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

      // Capture previous value so we can revert on error
      const previous = multiStepReasoningEnabled

      // Update local state for immediate UI feedback
      setLocalEnabled(checked)

      try {
        await updateMultiStepReasoning(currentSessionId, {
          multi_step_reasoning_enabled: checked
        })
      } catch {
        // On error, revert local state to the previous value
        setLocalEnabled(previous)
      }
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
