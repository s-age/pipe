import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Box } from '@/components/molecules/Box'
import { ScrollArea } from '@/components/molecules/ScrollArea'
import { ArtifactList } from '@/components/organisms/ArtifactList'
import { Form, useOptionalFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { MultiStepReasoning } from '@/components/organisms/MultiStepReasoning'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'
import { useSessionMetaLifecycle } from './hooks/useSessionMetaLifecycle'
import type { SessionMetaFormInputs } from './schema'
import { sessionMetaSchema } from './schema'
import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  stickySaveMetaButtonContainer,
  saveMetaButton,
  srOnly
} from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail
  onRefresh: () => Promise<void>
  onSessionDetailUpdate?: (sessionDetail: SessionDetail) => void
}

export const SessionMeta = ({
  sessionDetail,
  onRefresh,
  onSessionDetailUpdate
}: SessionMetaProperties): JSX.Element | null => {
  const { computedDefaultValues } = useSessionMetaLifecycle({
    sessionDetail
  })

  if (sessionDetail === null) {
    return null
  }

  const MetaContent = (): JSX.Element => {
    const formContext = useOptionalFormContext()

    const { handleSaveClick, isSubmitting, saveStatus } = useSessionMetaHandlers({
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
        {saveStatus !== 'idle' && (
          <div role="status" aria-live="polite" className={srOnly}>
            {saveStatus === 'success'
              ? 'Session metadata saved successfully'
              : 'Failed to save session metadata'}
          </div>
        )}
        <ScrollArea className={sessionMetaSection}>
          <Box padding="m" radius="m" className={sessionMetaView}>
            <SessionMetaBasic sessionDetail={sessionDetail} />
          </Box>

          <Box padding="m" radius="m" className={sessionMetaView}>
            <ReferenceList sessionDetail={sessionDetail} refreshSessions={onRefresh} />

            <ArtifactList sessionDetail={sessionDetail} refreshSessions={onRefresh} />

            <HyperParameters sessionDetail={sessionDetail} />

            <MultiStepReasoning
              multiStepReasoningEnabled={
                sessionDetail?.multiStepReasoningEnabled ?? false
              }
              currentSessionId={sessionDetail.sessionId ?? null}
            />

            <TodoList
              sessionDetail={sessionDetail}
              onSessionDetailUpdate={onSessionDetailUpdate}
            />
          </Box>
        </ScrollArea>

        <Box className={stickySaveMetaButtonContainer}>
          <Button
            kind="primary"
            size="default"
            type="submit"
            disabled={isSubmitting}
            onClick={handleSaveClick}
            className={saveMetaButton}
            aria-label="Save session metadata"
            aria-busy={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : 'Save Meta'}
          </Button>
        </Box>
      </>
    )
  }

  return (
    <Box className={metaColumn}>
      <Form<SessionMetaFormInputs>
        defaultValues={computedDefaultValues}
        schema={sessionMetaSchema}
      >
        <MetaContent />
      </Form>
    </Box>
  )
}
