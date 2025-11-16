import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Fieldset } from '@/components/molecules/Fieldset'
import { MultipleSelect } from '@/components/molecules/MultipleSelect'
import { TextArea } from '@/components/molecules/TextArea'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'

import { formContainer } from './style.css'
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
    <Heading level={1}>Create New Session</Heading>

    <SessionMetaBasic sessionDetail={sessionDetail} />

    <MultipleSelect name="parent" options={parentOptions} searchable={true} />

    <Fieldset legend={<span className={metaItemLabel}>First Instruction:</span>}>
      {(ids) => (
        <TextArea
          id="instruction"
          name="instruction"
          aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
        />
      )}
    </Fieldset>

    <ReferenceList sessionDetail={sessionDetail} />

    <HyperParameters sessionDetail={sessionDetail} />

    <TodoList sessionDetail={sessionDetail} />

    <Button
      type="button"
      kind="primary"
      size="default"
      disabled={isSubmitting}
      onClick={handleCreateClick}
    >
      {isSubmitting ? 'Creating...' : 'Create Session'}
    </Button>
    <Button type="button" kind="secondary" size="default" onClick={handleCancel}>
      Cancel
    </Button>
  </div>
)
