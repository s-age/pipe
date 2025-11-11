import type { JSX } from 'react'
import { useRef, useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionTreeLifecycle } from './hooks/useSessionTreeLifecycle'
import { SessionItem } from './SessionItem'
import { SessionTreeFooter } from './SessionTreeFooter'
import { sessionListColumn, sessionListContainer } from './style.css'
import { useSessionTreeHandlers } from './useSessionTreeHandlers'

type SessionTreeProperties = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}

export const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession
}: SessionTreeProperties): JSX.Element => {
  const { handleNewChatClick } = useSessionTreeHandlers()
  const sessionReferences = useRef<Map<string, HTMLLIElement>>(new Map())

  // Handle scroll to selected session on mount and selection change
  useSessionTreeLifecycle({
    currentSessionId,
    sessions,
    sessionReferences
  })

  const setSessionReference = useCallback(
    (sessionId: string) =>
      (element: HTMLLIElement | null): void => {
        if (element) {
          sessionReferences.current.set(sessionId, element)
        } else {
          sessionReferences.current.delete(sessionId)
        }
      },
    []
  )

  return (
    <div className={sessionListColumn}>
      <ul className={sessionListContainer}>
        {sessions.map((session) => {
          if (!session.session_id || typeof session.session_id !== 'string') {
            console.warn('Skipping session with invalid session_id:', session)

            return null // Invalid session, skip rendering
          }

          return (
            <SessionItem
              key={session.session_id}
              session={session}
              currentSessionId={currentSessionId || ''}
              selectSession={selectSession}
              ref={setSessionReference(session.session_id)}
            />
          )
        })}
      </ul>
      <SessionTreeFooter handleNewChatClick={handleNewChatClick} />
    </div>
  )
}
