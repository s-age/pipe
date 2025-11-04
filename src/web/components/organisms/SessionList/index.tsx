import { JSX } from 'react'

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

type SessionListProps = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  onSessionSelect: (sessionId: string) => void
}

const SessionList = ({
  sessions,
  currentSessionId,
  onSessionSelect,
}: SessionListProps): JSX.Element => (
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
          <li key={session.session_id} className={sessionListItem}>
            <a
              href={`/session/${session.session_id}`}
              className={`${sessionLink} ${session.session_id === currentSessionId ? sessionLinkActive : ''}`.trim()}
              onClick={(e) => {
                e.preventDefault()
                onSessionSelect(session.session_id)
              }}
            >
              {session.purpose}{' '}
              <p className={sessionIdStyle}>{session.session_id.substring(0, 8)}</p>
            </a>
          </li>
        )
      })}
    </ul>
    <div className={stickyNewChatButtonContainer}>
      <Button
        kind="primary"
        size="default"
        onClick={() => (window.location.href = '/start_session')}
      >
        + New Chat
      </Button>
    </div>
  </div>
)

export default SessionList
