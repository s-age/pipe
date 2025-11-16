import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Select } from '@/components/molecules/Select'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'

import { useStartSessionFormHandlers } from './hooks/useStartSessionFormHandlers'
import type { StartSessionFormInputs } from './schema'
import {
  formContainer,
  scrollable,
  headingSticky,
  fieldsetContainer,
  buttonBar,
  primaryButton,
  secondaryButton
} from './style.css'
import { metaItemLabel } from '../SessionMetaBasic/style.css'

type StartSessionFormInnerProperties = {
  sessionDetail: SessionDetail
  parentOptions: Option[]
}

export const StartSessionFormInner = ({
  sessionDetail,
  parentOptions
}: StartSessionFormInnerProperties): JSX.Element => {
  const formContext = useOptionalFormContext<StartSessionFormInputs>()
  const isSubmitting = formContext?.formState?.isSubmitting ?? false

  // formContext is available if this component is rendered inside a Form provider

  const { handleCancel, handleCreateClick } = useStartSessionFormHandlers()

  return (
    <div className={formContainer}>
      <div className={scrollable}>
        <Heading level={1} className={headingSticky}>
          Create New Session
        </Heading>

        <SessionMetaBasic sessionDetail={sessionDetail}>
          <Fieldset
            legend={<span className={metaItemLabel}>First Instruction:</span>}
            className={fieldsetContainer}
          >
            {(ids) => (
              <TextArea
                id="instruction"
                name="instruction"
                aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
              />
            )}
          </Fieldset>
        </SessionMetaBasic>

        <Fieldset
          legend={<span className={metaItemLabel}>Parent Session:</span>}
          className={fieldsetContainer}
        >
          <Select name="parent" options={parentOptions} searchable={true} />
        </Fieldset>

        <ReferenceList sessionDetail={sessionDetail} />

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
