import type { JSX } from 'react'

import { Strong } from '@/components/atoms/Strong'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { MetaItem } from '@/components/molecules/MetaItem'

import { useMultiStepReasoningHandlers } from './hooks/useMultiStepReasoningHandlers'
import { multiStepLabel } from './style.css'

type MultiStepReasoningProperties = {
  currentSessionId: string | null
  multiStepReasoningEnabled: boolean
}

export const MultiStepReasoning = ({
  currentSessionId,
  multiStepReasoningEnabled
}: MultiStepReasoningProperties): JSX.Element => {
  const { handleMultiStepReasoningChange, localEnabled } =
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
        <Strong className={multiStepLabel}>Multi-step Reasoning</Strong>
      </InputCheckbox>
    </MetaItem>
  )
}
