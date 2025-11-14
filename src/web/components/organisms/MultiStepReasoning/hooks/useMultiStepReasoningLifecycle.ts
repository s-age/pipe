import { useEffect, useState } from 'react'

export const useMultiStepReasoningLifecycle = (
  multiStepReasoningEnabled: boolean
): {
  localEnabled: boolean
  setLocalEnabled: React.Dispatch<React.SetStateAction<boolean>>
} => {
  const [localEnabled, setLocalEnabled] = useState(multiStepReasoningEnabled)

  // Update local state when prop changes
  useEffect(() => {
    setLocalEnabled(multiStepReasoningEnabled)
  }, [multiStepReasoningEnabled])

  return {
    localEnabled,
    setLocalEnabled
  }
}
