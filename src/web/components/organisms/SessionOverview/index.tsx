import clsx from 'clsx'
import { forwardRef } from 'react'

import { Link } from '@/components/molecules/Link'
import { ListItem } from '@/components/molecules/ListItem'
import { Paragraph } from '@/components/molecules/Paragraph'
import type { SessionOverview as SessionOverviewType } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionOverviewHandlers } from './hooks/useSessionOverviewHandlers'
import {
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle
} from './style.css'

type SessionOverviewProperties = {
  currentSessionId: string
  session: SessionOverviewType
  handleSelectSession: (sessionId: string) => Promise<void>
}

export const SessionOverviewComponent = forwardRef<
  HTMLLIElement,
  SessionOverviewProperties
>(({ currentSessionId, handleSelectSession, session }, reference) => {
  const { onClick } = useSessionOverviewHandlers({ session, handleSelectSession })

  return (
    <ListItem key={session.sessionId} className={sessionListItem} ref={reference}>
      <Link
        href={`/session/${session.sessionId}`}
        className={clsx(sessionLink, {
          [sessionLinkActive]: session.sessionId === currentSessionId
        })}
        onClick={onClick}
      >
        {session.purpose}{' '}
        <Paragraph className={sessionIdStyle}>
          {session.sessionId.substring(0, 8)}
        </Paragraph>
      </Link>
    </ListItem>
  )
})

SessionOverviewComponent.displayName = 'SessionOverviewComponent'
