import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { useSessionMetaForm } from '@/components/organisms/SessionMeta/hooks/useSessionMetaForm'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Actions } from '@/stores/useChatHistoryStore'

import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  stickySaveMetaButtonContainer
} from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
  actions: Actions
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  refreshSessions,
  actions
}: SessionMetaProperties): React.JSX.Element => {
  const { defaultValues, onSubmit, isSubmitting, saved } = useSessionMetaForm({
    sessionDetail,
    currentSessionId,
    actions
  })

  return (
    <Form defaultValues={defaultValues} onSubmit={onSubmit}>
      <div className={metaColumn}>
        <input type="hidden" id="current-session-id" value={currentSessionId ?? ''} />
        <section className={sessionMetaSection}>
          <div className={sessionMetaView}>
            <SessionMetaBasic
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              refreshSessions={refreshSessions}
              setSessionDetail={setSessionDetail}
            />

            <ReferenceList
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              setSessionDetail={setSessionDetail}
              refreshSessions={refreshSessions}
            />

            <HyperParameters
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              actions={actions}
            />

            <TodoList
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              setSessionDetail={setSessionDetail}
              refreshSessions={refreshSessions}
            />
          </div>
        </section>

        <div className={stickySaveMetaButtonContainer}>
          <Button kind="primary" size="default" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Meta'}
          </Button>
          {saved ? <span>Saved</span> : null}
        </div>
      </div>
    </Form>
  )
}
