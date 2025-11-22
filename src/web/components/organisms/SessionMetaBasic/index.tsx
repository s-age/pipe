import type { JSX, ReactNode } from 'react'
import React from 'react'

import { ArtifactsSelector } from '@/components/molecules/ArtifactsSelector'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputText } from '@/components/molecules/InputText'
import { MetaLabel } from '@/components/molecules/MetaItem'
import { MetaItem } from '@/components/molecules/MetaItem'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'
import { ProcedureSelect } from '@/components/organisms/ProcedureSelect'
import { RolesSelect } from '@/components/organisms/RolesSelect'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionMetaBasicSync } from './hooks/useSessionMetaBasicSync'
import { inputFullWidth } from './style.css'

type SessionMetaBasicProperties = {
  sessionDetail: SessionDetail
  children?: ReactNode
}

export const SessionMetaBasic = ({
  sessionDetail,
  children
}: SessionMetaBasicProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const register = formContext?.register
  const setValue = formContext?.setValue
  const errors = formContext?.formState?.errors
  const isSubmitting = formContext?.formState?.isSubmitting

  const handleRolesChange = React.useCallback(
    (roles: string[]) => {
      setValue?.('roles', roles)
    },
    [setValue]
  )

  useSessionMetaBasicSync(sessionDetail, formContext, isSubmitting)

  return (
    <>
      <MetaItem>
        <Fieldset
          legend={<MetaLabel required={true}>Purpose:</MetaLabel>}
          error={errors?.purpose as unknown as React.ReactNode}
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
      </MetaItem>

      <MetaItem>
        <Fieldset
          legend={<MetaLabel required={true}>Background:</MetaLabel>}
          error={errors?.background as unknown as React.ReactNode}
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
      </MetaItem>

      {children}

      <MetaItem>
        <Fieldset legend={<MetaLabel>Roles:</MetaLabel>}>
          {(ids) => (
            <RolesSelect
              placeholder="Select roles"
              sessionDetail={sessionDetail}
              onChange={handleRolesChange}
              aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
            />
          )}
        </Fieldset>
      </MetaItem>

      <MetaItem>
        <Fieldset legend={<MetaLabel>Procedure:</MetaLabel>}>
          <ProcedureSelect placeholder="Select procedure" />
        </Fieldset>
      </MetaItem>

      <ArtifactsSelector />
    </>
  )
}
