import React from 'react'

import { ArtifactsSelector } from '@/components/molecules/ArtifactsSelector'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputText } from '@/components/molecules/InputText'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'
import { ProcedureSelect } from '@/components/organisms/ProcedureSelect'
import { RolesSelect } from '@/components/organisms/RolesSelect'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { metaItem, metaItemLabel, inputFullWidth } from './style.css'

type SessionMetaBasicProperties = {
  sessionDetail: SessionDetail
  _setError?: (error: string | null) => void
}

export const SessionMetaBasic = ({
  sessionDetail
}: SessionMetaBasicProperties): React.JSX.Element => {
  const formContext = useOptionalFormContext()
  const register = formContext?.register
  const setValue = formContext?.setValue

  const handleRolesChange = React.useCallback(
    (roles: string[]) => {
      setValue?.('roles', roles)
    },
    [setValue]
  )

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
            className={inputFullWidth}
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
            placeholder="Select roles"
            sessionDetail={sessionDetail}
            onChange={handleRolesChange}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Procedure:</span>}
        className={metaItem}
      >
        <ProcedureSelect placeholder="Select procedure" />
      </Fieldset>

      <ArtifactsSelector />
    </>
  )
}
