import { JSX, useCallback } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import { getSession, SessionDetail } from '@/lib/api/session/getSession'
import { SessionOverview } from '@/lib/api/sessionTree/getSessions'

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

type SessionItemProps = {
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
}: SessionItemProps): JSX.Element => {
  const onClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()

      if (typeof session.session_id !== 'string') {
        setError('Invalid session ID.')

        return
      }

      try {
        const sessionDetail = await getSession(session.session_id)
        selectSession(session.session_id, sessionDetail.session)
        window.history.replaceState({}, '', `/session/${session.session_id}`)
      } catch (error) {
        setError((error as Error).message || 'Failed to load session data.')
      }
    },
    [selectSession, session.session_id, setError],
  )

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

type SessionTreeProps = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  setError: (errorMessage: string | null) => void
}

const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession,
  setError,
}: SessionTreeProps): JSX.Element => {
  const { handleNewChatClick } = useSessionTreeHandlers()

  return (
    <div className={sessionListColumn}>
      <Heading level={2} className={h2Style}>
        Sessions
      </Heading>
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

export default SessionTree
