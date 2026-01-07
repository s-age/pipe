import { clsx } from 'clsx'
import { forwardRef } from 'react'

import { Link } from '@/components/molecules/Link'
import { ListItem } from '@/components/molecules/ListItem'
import { Paragraph } from '@/components/molecules/Paragraph'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle
} from './style.css'

type SessionItemProperties = {
  currentSessionId: string
  session: SessionOverview
  handleSelectSession: (sessionId: string) => Promise<void>
}

export const SessionItem = forwardRef<HTMLLIElement, SessionItemProperties>(
  ({ currentSessionId, handleSelectSession, session }, reference) => {
    const { onClick } = useSessionItemHandlers({ session, handleSelectSession })

    return (
      <ListItem key={session.sessionId} className={sessionListItem} ref={reference}>
        <Link
          href={`/session/${session.sessionId}`}
          className={clsx(
            sessionLink,
            session.sessionId === currentSessionId && sessionLinkActive
          )}
          onClick={onClick}
        >
          {session.purpose}{' '}
          <Paragraph className={sessionIdStyle}>
            {session.sessionId.substring(0, 8)}
          </Paragraph>
        </Link>
      </ListItem>
    )
  }
)

SessionItem.displayName = 'SessionItem'
