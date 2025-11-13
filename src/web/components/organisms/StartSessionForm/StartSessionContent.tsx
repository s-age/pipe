import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Fieldset } from '@/components/molecules/Fieldset'
import { TextArea } from '@/components/molecules/TextArea'
import { useFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'

import type { StartSessionFormInputs } from './schema'
import { formContainer } from './style.css'
import { metaItemLabel } from '../SessionMetaBasic/style.css'

type StartSessionContentProperties = {
  handleCancel: () => void
  handleCreateClick: () => void
  noop: () => Promise<void>
  noopSetSessionDetail: (_data: SessionDetail | null) => void
  noopOnSessionUpdate: (_data: SessionDetail | null) => void
}

export const StartSessionContent = ({
  handleCancel,
  handleCreateClick,
  noop,
  noopSetSessionDetail,
  noopOnSessionUpdate
}: StartSessionContentProperties): JSX.Element => {
  const {
    formState: { isSubmitting }
  } = useFormContext<StartSessionFormInputs>()

  return (
    <div className={formContainer}>
      <Heading level={1}>Create New Session</Heading>

      <SessionMetaBasic sessionDetail={null} currentSessionId={null} onRefresh={noop} />

      <Fieldset legend={<span className={metaItemLabel}>First Instruction:</span>}>
        {(ids) => (
          <TextArea
            id="instruction"
            name="instruction"
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <ReferenceList
        sessionDetail={null}
        currentSessionId={null}
        setSessionDetail={noopSetSessionDetail}
      />

      <HyperParameters
        sessionDetail={null}
        currentSessionId={null}
        onSessionUpdate={noopOnSessionUpdate}
      />

      <TodoList sessionDetail={null} currentSessionId={null} />

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
}
