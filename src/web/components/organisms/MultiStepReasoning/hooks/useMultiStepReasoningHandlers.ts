import { useCallback, useEffect, useState } from 'react'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  multiStepReasoningEnabled: boolean
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  multiStepReasoningEnabled
}: UseMultiStepReasoningHandlersProperties): {
  localEnabled: boolean
  setLocalEnabled: React.Dispatch<React.SetStateAction<boolean>>
  handleMultiStepReasoningChange: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => Promise<void>
} => {
  const [localEnabled, setLocalEnabled] = useState(multiStepReasoningEnabled)

  // Update local state when prop changes
  useEffect(() => {
    setLocalEnabled(multiStepReasoningEnabled)
  }, [multiStepReasoningEnabled])
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
          multiStepReasoningEnabled: checked
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

  return { localEnabled, setLocalEnabled, handleMultiStepReasoningChange }
}
