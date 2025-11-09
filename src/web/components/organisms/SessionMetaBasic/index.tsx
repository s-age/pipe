import React from 'react'

import { InputCheckbox } from '@/components/atoms/InputCheckbox'
import { InputText } from '@/components/atoms/InputText'
import { TextArea } from '@/components/atoms/TextArea'
import { Fieldset } from '@/components/molecules/Fieldset'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useMultiStepReasoningHandlers } from './hooks/useMultiStepReasoningHandlers'
import {
  metaItem,
  multiStepLabel,
  metaItemLabel,
  inputFullWidth,
  textareaFullWidth
} from './style.css'

type SessionMetaBasicProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  _setError?: (error: string | null) => void
  refreshSessions: () => Promise<void>
  setSessionDetail?: (data: SessionDetail | null) => void
}

export const SessionMetaBasic = ({
  sessionDetail,
  currentSessionId,
  refreshSessions,
  setSessionDetail
}: SessionMetaBasicProperties): React.JSX.Element => {
  const register = useOptionalFormContext()?.register
  const { handleMultiStepReasoningChange } = useMultiStepReasoningHandlers({
    currentSessionId,
    sessionDetail,
    refreshSessions,
    setSessionDetail
  })

  return (
    <>
      <Fieldset
        legend={<span className={metaItemLabel}>Purpose:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="purpose"
            register={register}
            name="purpose"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Background:</span>}
        className={metaItem}
      >
        {(ids) => (
          <TextArea
            id="background"
            register={register}
            name="background"
            className={textareaFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Roles:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="roles"
            register={register}
            name="roles"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Procedure:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="procedure"
            register={register}
            name="procedure"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Artifacts:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="artifacts"
            register={register}
            name="artifacts"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <div className={metaItem}>
        <InputCheckbox
          name="multi_step_reasoning"
          checked={sessionDetail?.multi_step_reasoning_enabled ?? false}
          onChange={handleMultiStepReasoningChange}
        >
          <strong className={multiStepLabel}>Multi-step Reasoning</strong>
        </InputCheckbox>
      </div>
    </>
  )
}
