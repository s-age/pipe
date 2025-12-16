import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type {
  SessionOverview,
  SessionTreeNode as SessionTreeNodeType
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionTreeHandlers } from './hooks/useSessionTreeHandlers'
import { useSessionTreeLifecycle } from './hooks/useSessionTreeLifecycle'
import { SessionTreeFooter } from './SessionTreeFooter'
import { SessionTreeNode } from './SessionTreeNode'
import { sessionListColumn, sessionListContainer } from './style.css'
import { SessionOverviewComponent } from '../SessionOverview'

type SessionTreeProperties = {
  // sessions may be a flat array of SessionOverview or hierarchical nodes
  sessions: SessionOverview[] | SessionTreeNodeType[]
  currentSessionId: string | null
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  onRefresh: () => Promise<void>
}

export const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession,
  onRefresh
}: SessionTreeProperties): JSX.Element => {
  const {
    sessionReferences,
    handleNewChatClick,
    handleAnchorClick,
    setSessionReference
  } = useSessionTreeHandlers(onRefresh)

  // Handle scroll to selected session on mount and selection change
  useSessionTreeLifecycle({
    currentSessionId,
    sessions,
    sessionReferences
  })

  // ref management delegated to handlers via `setSessionReference`.

  return (
    <div className={sessionListColumn}>
      <ul className={sessionListContainer}>
        {Array.isArray(sessions) &&
        sessions.length > 0 &&
        'overview' in (sessions[0] as SessionOverview | SessionTreeNodeType)
          ? // hierarchical nodes: render recursively
            (sessions as SessionTreeNodeType[]).map((node: SessionTreeNodeType) => (
              <SessionTreeNode
                key={node.sessionId}
                node={node}
                currentSessionId={currentSessionId}
                handleAnchorClick={handleAnchorClick}
                setSessionReference={setSessionReference}
              />
            ))
          : // flat list: render as before
            (sessions as SessionOverview[]).map((session) => {
              if (!session.sessionId || typeof session.sessionId !== 'string') {
                return null // Invalid session, skip rendering
              }

              return (
                <SessionOverviewComponent
                  key={session.sessionId}
                  session={session}
                  currentSessionId={currentSessionId || ''}
                  selectSession={selectSession}
                  ref={setSessionReference(session.sessionId)}
                />
              )
            })}
      </ul>
      <SessionTreeFooter handleNewChatClick={handleNewChatClick} />
    </div>
  )
}
