import type { JSX } from 'react'
import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { useSessionMetaHandlers } from '@/components/organisms/SessionMeta/hooks/useSessionMetaHandlers'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

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
  onRefresh: () => Promise<void>
  roleOptions: RoleOption[]
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  onRefresh,
  roleOptions
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
      void handleSubmit(onSubmit)()
    }, [handleSubmit])

    return (
      <div className={metaColumn}>
        <input type="hidden" id="current-session-id" value={currentSessionId ?? ''} />
        <section className={sessionMetaSection}>
          <div className={sessionMetaView}>
            <SessionMetaBasic
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              onRefresh={onRefresh}
              roleOptions={roleOptions}
            />

            <ReferenceList
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              setSessionDetail={setSessionDetail}
              refreshSessions={onRefresh}
            />

            <HyperParameters
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              onSessionUpdate={setSessionDetail}
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
      </div>
    )
  }

  return (
    <Form defaultValues={defaultValues}>
      <MetaContent />
    </Form>
  )
}
