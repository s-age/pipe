import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import {
  sessionListColumn,
  sessionListContainer,
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle,
  stickyNewChatButtonContainer,
} from './style.css'
import { useSessionTreeHandlers } from './useSessionTreeHandlers'

type SessionItemProperties = {
  session: SessionOverview
  currentSessionId: string
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  setError: (errorMessage: string | null) => void
}

const SessionItem = ({
  session,
  currentSessionId,
  selectSession,
  setError,
}: SessionItemProperties): JSX.Element => {
  const { onClick } = useSessionItemHandlers({ session, selectSession, setError })

  return (
    <li key={session.session_id} className={sessionListItem}>
      <a
        href={`/session/${session.session_id}`}
        className={`${sessionLink} ${session.session_id === currentSessionId ? sessionLinkActive : ''}`.trim()}
        onClick={onClick}
      >
        {session.purpose}{' '}
        <p className={sessionIdStyle}>{session.session_id.substring(0, 8)}</p>
      </a>
    </li>
  )
}

type SessionTreeProperties = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  setError: (errorMessage: string | null) => void
}

export const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession,
  setError,
}: SessionTreeProperties): JSX.Element => {
  const { handleNewChatClick } = useSessionTreeHandlers()

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
              setError={setError}
            />
          )
        })}
      </ul>
      <div className={stickyNewChatButtonContainer}>
        <Button kind="primary" size="default" onClick={handleNewChatClick}>
          + New Chat
        </Button>
      </div>
    </div>
  )
}
