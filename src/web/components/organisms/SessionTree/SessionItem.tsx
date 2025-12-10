import { forwardRef } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle
} from './style.css'

type SessionItemProperties = {
  session: SessionOverview
  currentSessionId: string
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}

export const SessionItem = forwardRef<HTMLLIElement, SessionItemProperties>(
  ({ session, currentSessionId, selectSession }, reference) => {
    const { onClick } = useSessionItemHandlers({ session, selectSession })

    return (
      <li key={session.sessionId} className={sessionListItem} ref={reference}>
        <a
          href={`/session/${session.sessionId}`}
          className={`${sessionLink} ${session.sessionId === currentSessionId ? sessionLinkActive : ''}`.trim()}
          onClick={onClick}
        >
          {session.purpose}{' '}
          <p className={sessionIdStyle}>{session.sessionId.substring(0, 8)}</p>
        </a>
      </li>
    )
  }
)

SessionItem.displayName = 'SessionItem'
