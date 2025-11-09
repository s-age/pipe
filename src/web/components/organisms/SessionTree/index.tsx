import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

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
  selectSession,
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
            />
          )
        })}
      </ul>
      <SessionTreeFooter handleNewChatClick={handleNewChatClick} />
    </div>
  )
}
