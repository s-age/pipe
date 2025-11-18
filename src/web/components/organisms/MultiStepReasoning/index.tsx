import type { JSX } from 'react'

import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { metaItem, multiStepLabel } from '@/styles/sessionMeta.css'

import { useMultiStepReasoningHandlers } from './hooks/useMultiStepReasoningHandlers'
import { useMultiStepReasoningLifecycle } from './hooks/useMultiStepReasoningLifecycle'

type MultiStepReasoningProperties = {
  multiStepReasoningEnabled: boolean
  currentSessionId: string | null
}

export const MultiStepReasoning = ({
  multiStepReasoningEnabled,
  currentSessionId
}: MultiStepReasoningProperties): JSX.Element => {
  const { localEnabled, setLocalEnabled } = useMultiStepReasoningLifecycle(
    multiStepReasoningEnabled
  )

  const { handleMultiStepReasoningChange } = useMultiStepReasoningHandlers({
    currentSessionId,
    multiStepReasoningEnabled,
    setLocalEnabled
  })

  return (
    <div className={metaItem}>
      <InputCheckbox checked={localEnabled} onChange={handleMultiStepReasoningChange}>
        <strong className={multiStepLabel}>Multi-step Reasoning</strong>
      </InputCheckbox>
    </div>
  )
}
