import { useEffect } from 'react'

export type UseMultiStepReasoningLifecycleProperties = {
  multiStepReasoningEnabled: boolean
  setLocalEnabled: React.Dispatch<React.SetStateAction<boolean>>
}

/**
 * useMultiStepReasoningLifecycle
 *
 * Manages MultiStepReasoning lifecycle effects (sync from props).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useMultiStepReasoningLifecycle = ({
  multiStepReasoningEnabled,
  setLocalEnabled
}: UseMultiStepReasoningLifecycleProperties): void => {
  // Update local state when prop changes
  useEffect(() => {
    setLocalEnabled(multiStepReasoningEnabled)
  }, [multiStepReasoningEnabled, setLocalEnabled])
}
