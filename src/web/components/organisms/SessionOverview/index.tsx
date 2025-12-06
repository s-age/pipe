import { forwardRef } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview as SessionOverviewType } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionOverviewHandlers } from './hooks/useSessionOverviewHandlers'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle
} from './style.css'

type SessionOverviewProperties = {
  session: SessionOverviewType
  currentSessionId: string
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}

export const SessionOverviewComponent = forwardRef<
  HTMLLIElement,
  SessionOverviewProperties
>(({ session, currentSessionId, selectSession }, reference) => {
  const { onClick } = useSessionOverviewHandlers({ session, selectSession })

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
})

SessionOverviewComponent.displayName = 'SessionOverviewComponent'
