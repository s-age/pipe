import type { JSX } from 'react'
import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Form, useOptionalFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { MultiStepReasoning } from '@/components/organisms/MultiStepReasoning'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'

// eslint-disable-next-line import/order
import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'

type SessionMetaFormInputs = {
  purpose: string | null
  background: string | null
  roles: string[] | null
  procedure: string | null
  references: {
    path: string
    ttl: number | null
    persist: boolean
    disabled: boolean
  }[]
  artifacts: string[] | null
  hyperparameters: {
    temperature: number | null
    top_p: number | null
    top_k: number | null
  } | null
  multi_step_reasoning: boolean
}
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
    const formContext = useOptionalFormContext()

    const handleSaveClick = React.useCallback((): void => {
      void formContext?.handleSubmit(onSubmit as never)()
    }, [formContext])

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
            type="submit"
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
