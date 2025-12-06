import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Form, useOptionalFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { MultiStepReasoning } from '@/components/organisms/MultiStepReasoning'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'
// eslint-disable-next-line import/order
import { useSessionMetaLifecycle } from './hooks/useSessionMetaLifecycle'

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
    topP: number | null
    topK: number | null
  } | null
  multiStepReasoning: boolean
}
import { sessionMetaSchema } from './schema'
import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  stickySaveMetaButtonContainer,
  saveMetaButton
} from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail
  onRefresh: () => Promise<void>
}

export const SessionMeta = ({
  sessionDetail,
  onRefresh
}: SessionMetaProperties): JSX.Element | null => {
  const { computedDefaultValues } = useSessionMetaLifecycle({
    sessionDetail
  })

  if (sessionDetail === null) {
    return null
  }

  const MetaContent = (): JSX.Element => {
    const formContext = useOptionalFormContext()

    const { isSubmitting, handleSaveClick } = useSessionMetaHandlers({
      sessionDetail,
      onRefresh,
      formContext
    })

    return (
      <>
        <input
          type="hidden"
          id="current-session-id"
          value={sessionDetail?.sessionId ?? ''}
        />
        <section className={sessionMetaSection}>
          <div className={sessionMetaView}>
            <SessionMetaBasic sessionDetail={sessionDetail} />
          </div>

          <div className={sessionMetaView}>
            <ReferenceList sessionDetail={sessionDetail} />

            <HyperParameters sessionDetail={sessionDetail} />

            <MultiStepReasoning
              multiStepReasoningEnabled={
                sessionDetail?.multiStepReasoningEnabled ?? false
              }
              currentSessionId={sessionDetail.sessionId ?? null}
            />

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
            className={saveMetaButton}
          >
            {isSubmitting ? 'Saving...' : 'Save Meta'}
          </Button>
        </div>
      </>
    )
  }

  return (
    <div className={metaColumn}>
      <Form<SessionMetaFormInputs>
        defaultValues={computedDefaultValues}
        schema={sessionMetaSchema}
      >
        <MetaContent />
      </Form>
    </div>
  )
}
