import React from 'react'

import { Fieldset } from '@/components/molecules/Fieldset'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { InputText } from '@/components/molecules/InputText'
import { RolesSelect } from '@/components/molecules/RolesSelect'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { RoleOption } from '@/lib/api/roles/getRoles'
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
  onRefresh: () => Promise<void>
  setSessionDetail?: (data: SessionDetail | null) => void
  roleOptions: RoleOption[]
}

export const SessionMetaBasic = ({
  sessionDetail,
  currentSessionId,
  onRefresh,
  setSessionDetail,
  roleOptions
}: SessionMetaBasicProperties): React.JSX.Element => {
  const register = useOptionalFormContext()?.register
  const { handleMultiStepReasoningChange } = useMultiStepReasoningHandlers({
    currentSessionId,
    sessionDetail,
    onRefresh,
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
          <RolesSelect
            id="roles"
            register={register}
            name="roles"
            placeholder="Select roles"
            sessionDetail={sessionDetail}
            roleOptions={roleOptions}
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
