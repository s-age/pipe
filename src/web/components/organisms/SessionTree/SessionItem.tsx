import { clsx } from 'clsx'
import { forwardRef } from 'react'

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
  handleSelectSession: (sessionId: string) => Promise<void>
}

export const SessionItem = forwardRef<HTMLLIElement, SessionItemProperties>(
  ({ session, currentSessionId, handleSelectSession }, reference) => {
    const { onClick } = useSessionItemHandlers({ session, handleSelectSession })

    return (
      <li key={session.sessionId} className={sessionListItem} ref={reference}>
        <a
          href={`/session/${session.sessionId}`}
          className={clsx(
            sessionLink,
            session.sessionId === currentSessionId && sessionLinkActive
          )}
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
