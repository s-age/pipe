import type { JSX } from 'react'
import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { MultiStepReasoning } from '@/components/organisms/MultiStepReasoning'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'
import type { SessionMetaFormInputs } from './schema'
import { sessionMetaSchema } from './schema'
import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  stickySaveMetaButtonContainer
} from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail
  onRefresh: () => Promise<void>
}

export const SessionMeta = ({
  sessionDetail,
  onRefresh
}: SessionMetaProperties): JSX.Element | null => {
  const { defaultValues, onSubmit, isSubmitting, saved } = useSessionMetaHandlers({
    sessionDetail,
    onRefresh
  })

  if (sessionDetail === null) {
    return null
  }

  const MetaContent = (): JSX.Element => {
    const { handleSubmit } = useFormContext()

    const handleSaveClick = React.useCallback((): void => {
      void handleSubmit(onSubmit as never)()
    }, [handleSubmit])

    return (
      <>
        <input
          type="hidden"
          id="current-session-id"
          value={sessionDetail?.session_id ?? ''}
        />
        <section className={sessionMetaSection}>
          <div className={sessionMetaView}>
            <SessionMetaBasic sessionDetail={sessionDetail} />
          </div>

          <div className={sessionMetaView}>
            <MultiStepReasoning
              multiStepReasoningEnabled={
                sessionDetail?.multi_step_reasoning_enabled ?? false
              }
              currentSessionId={sessionDetail.session_id ?? null}
            />

            <ReferenceList sessionDetail={sessionDetail} />

            <HyperParameters sessionDetail={sessionDetail} />

            <TodoList sessionDetail={sessionDetail} />
          </div>
        </section>

        <div className={stickySaveMetaButtonContainer}>
          <Button
            kind="primary"
            size="default"
            type="button"
            disabled={isSubmitting}
            onClick={handleSaveClick}
          >
            {isSubmitting ? 'Saving...' : 'Save Meta'}
          </Button>
          {saved ? <span>Saved</span> : null}
        </div>
      </>
    )
  }

  return (
    <div className={metaColumn}>
      <Form<SessionMetaFormInputs>
        defaultValues={defaultValues}
        schema={sessionMetaSchema}
      >
        <MetaContent />
      </Form>
    </div>
  )
}
