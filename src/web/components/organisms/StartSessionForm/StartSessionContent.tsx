import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Fieldset } from '@/components/molecules/Fieldset'
import { MultipleSelect } from '@/components/molecules/MultipleSelect'
import { TextArea } from '@/components/molecules/TextArea'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'

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

type StartSessionContentProperties = {
  sessionDetail: SessionDetail
  handleCancel: () => void
  handleCreateClick: () => void
  parentOptions: Option[]
  isSubmitting: boolean
}

export const StartSessionContent = ({
  sessionDetail,
  handleCancel,
  handleCreateClick,
  parentOptions,
  isSubmitting
}: StartSessionContentProperties): JSX.Element => (
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
        <MultipleSelect name="parent" options={parentOptions} searchable={true} />
      </Fieldset>

      <ReferenceList sessionDetail={sessionDetail} />

      <HyperParameters sessionDetail={sessionDetail} />

      <div className={buttonBar}>
        <Button
          type="button"
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
