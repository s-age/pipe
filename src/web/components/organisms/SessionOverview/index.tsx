import { forwardRef } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview as SessionOverviewType } from '@/lib/api/sessionTree/getSessionTree'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle
} from '@/styles/sessionTree.css'

import { useSessionOverviewHandlers } from './hooks/useSessionOverviewHandlers'

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
    <li key={session.session_id} className={sessionListItem} ref={reference}>
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
})

SessionOverviewComponent.displayName = 'SessionOverviewComponent'
