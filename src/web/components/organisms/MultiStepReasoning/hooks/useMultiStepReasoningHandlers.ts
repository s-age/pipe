import { useCallback, useState } from 'react'

import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'
import { useMultiStepReasoningLifecycle } from './useMultiStepReasoningLifecycle'

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

  // Lifecycle: sync props to local state
  useMultiStepReasoningLifecycle({ multiStepReasoningEnabled, setLocalEnabled })

  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleMultiStepReasoningChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      const checked = event.target.checked

      // Update local state for immediate UI feedback
      setLocalEnabled(checked)

      // Only call API if we have a valid session ID
      if (currentSessionId) {
        await updateMultiStepReasoning(currentSessionId, {
          multiStepReasoningEnabled: checked
        })
      }
    },
    [currentSessionId, updateMultiStepReasoning, setLocalEnabled]
  )

  return { localEnabled, setLocalEnabled, handleMultiStepReasoningChange }
}
