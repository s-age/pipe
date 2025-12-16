import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Fieldset } from '@/components/molecules/Fieldset'
import { MetaLabel } from '@/components/molecules/MetaItem'
import { Select } from '@/components/molecules/Select'
import { TextArea } from '@/components/molecules/TextArea'
// form context is accessed inside handlers when needed
import { useOptionalFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'

import { useStartSessionFormHandlers } from './hooks/useStartSessionFormHandlers'
import {
  formContainer,
  scrollable,
  headingSticky,
  fieldsetContainer,
  buttonBar,
  primaryButton,
  secondaryButton
} from './style.css'

type StartSessionFormInnerProperties = {
  sessionDetail: SessionDetail
  parentOptions: Option[]
}

export const StartSessionFormInner = ({
  sessionDetail,
  parentOptions
}: StartSessionFormInnerProperties): JSX.Element => {
  // Prefer the handler-provided submitting state to avoid relying on the
  // react-hook-form internal `formState.isSubmitting` which may not update
  // when native form submission is prevented or when navigation happens
  // quickly after submit. The hook will manage a local `isSubmitting` flag.
  const { handleCancel, handleCreateClick, dummyHandler, isSubmitting } =
    useStartSessionFormHandlers()

  const formContext = useOptionalFormContext()
  const register = formContext?.register
  const errors = formContext?.formState?.errors

  // Debug exposure removed.

  return (
    <div className={formContainer}>
      <div className={scrollable}>
        <Heading level={1} className={headingSticky}>
          Create New Session
        </Heading>

        <SessionMetaBasic sessionDetail={sessionDetail}>
          <Fieldset
            legend={<MetaLabel required={true}>First Instruction:</MetaLabel>}
            className={fieldsetContainer}
            error={
              errors?.instruction?.message
                ? String(errors.instruction.message)
                : undefined
            }
          >
            {(ids) => (
              <TextArea
                id="instruction"
                name="instruction"
                register={register}
                aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
              />
            )}
          </Fieldset>
        </SessionMetaBasic>

        <Fieldset
          legend={<MetaLabel>Parent Session:</MetaLabel>}
          className={fieldsetContainer}
          error={errors?.parent?.message ? String(errors.parent.message) : undefined}
        >
          <Select
            name="parent"
            options={parentOptions}
            register={register}
            searchable={true}
          />
        </Fieldset>

        <ReferenceList sessionDetail={sessionDetail} refreshSessions={dummyHandler} />

        <HyperParameters sessionDetail={sessionDetail} />

        <div className={buttonBar}>
          <Button
            type="submit"
            kind="primary"
            size="large"
            disabled={isSubmitting}
            onClick={handleCreateClick}
            className={primaryButton}
          >
            {isSubmitting ? 'Creating...' : 'Create Session'}
          </Button>

          <Button
            type="button"
            kind="secondary"
            size="default"
            onClick={handleCancel}
            className={secondaryButton}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}
