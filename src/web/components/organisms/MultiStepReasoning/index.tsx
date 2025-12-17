import type { JSX } from 'react'

import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { MetaItem } from '@/components/molecules/MetaItem'

import { useMultiStepReasoningHandlers } from './hooks/useMultiStepReasoningHandlers'
import { multiStepLabel } from './style.css'

type MultiStepReasoningProperties = {
  multiStepReasoningEnabled: boolean
  currentSessionId: string | null
}

export const MultiStepReasoning = ({
  multiStepReasoningEnabled,
  currentSessionId
}: MultiStepReasoningProperties): JSX.Element => {
  const { localEnabled, handleMultiStepReasoningChange } =
    useMultiStepReasoningHandlers({
      currentSessionId,
      multiStepReasoningEnabled
    })

  return (
    <MetaItem>
      <InputCheckbox
        name="multiStepReasoningEnabled"
        checked={localEnabled}
        onChange={handleMultiStepReasoningChange}
      >
        <strong className={multiStepLabel}>Multi-step Reasoning</strong>
      </InputCheckbox>
    </MetaItem>
  )
}
