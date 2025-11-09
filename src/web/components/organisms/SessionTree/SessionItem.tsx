import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle,
} from './style.css'

type SessionItemProperties = {
  session: SessionOverview
  currentSessionId: string
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  setError: (errorMessage: string | null) => void
}

export const SessionItem = ({
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
