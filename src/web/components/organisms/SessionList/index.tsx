import { JSX, useCallback } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import { SessionOverview } from '@/lib/api/sessions/getSessions'

import {
  sessionListColumn,
  sessionListContainer,
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle,
  stickyNewChatButtonContainer,
} from './style.css'
import { useSessionListHandlers } from './useSessionListHandlers'

type SessionItemProps = {
  session: SessionOverview
  currentSessionId: string
  handleSessionSelect: (sessionId: string) => void
}

const SessionItem = ({
  session,
  currentSessionId,
  handleSessionSelect,
}: SessionItemProps): JSX.Element => {
  const onClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>): void => {
      event.preventDefault()
      handleSessionSelect(session.session_id)
    },
    [session.session_id, handleSessionSelect],
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

type SessionListProps = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  handleSessionSelect: (sessionId: string) => void
}

const SessionList = ({
  sessions,
  currentSessionId,
  handleSessionSelect,
}: SessionListProps): JSX.Element => {
  const { handleNewChatClick } = useSessionListHandlers()

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
              handleSessionSelect={handleSessionSelect}
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

export default SessionList
