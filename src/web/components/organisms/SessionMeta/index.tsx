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
import { sessionMetaSchema } from './schema'
import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  stickySaveMetaButtonContainer
} from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onRefresh: () => Promise<void>
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  onRefresh
}: SessionMetaProperties): JSX.Element | null => {
  const { defaultValues, onSubmit, isSubmitting, saved } = useSessionMetaHandlers({
    sessionDetail,
    currentSessionId,
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
        <input type="hidden" id="current-session-id" value={currentSessionId ?? ''} />
        <section className={sessionMetaSection}>
          <div className={sessionMetaView}>
            <SessionMetaBasic sessionDetail={sessionDetail} />
          </div>

          <div className={sessionMetaView}>
            <MultiStepReasoning
              multiStepReasoningEnabled={
                sessionDetail?.multi_step_reasoning_enabled ?? false
              }
              currentSessionId={currentSessionId}
            />

            <ReferenceList currentSessionId={currentSessionId} />

            <HyperParameters
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
            />

            <TodoList
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
            />
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
      <Form defaultValues={defaultValues} schema={sessionMetaSchema}>
        <MetaContent />
      </Form>
    </div>
  )
}
