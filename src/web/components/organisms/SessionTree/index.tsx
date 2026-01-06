import type { JSX } from 'react'

import type {
  SessionOverview,
  SessionTreeNode as SessionTreeNodeType
} from '@/lib/api/sessionTree/getSessionTree'

import {
  useSessionTreeHandlers,
  type UseSessionTreeHandlersReturn
} from './hooks/useSessionTreeHandlers'
import { useSessionTreeLifecycle } from './hooks/useSessionTreeLifecycle'
import { SessionTreeFooter } from './SessionTreeFooter'
import { SessionTreeNode } from './SessionTreeNode'
import { sessionListColumn, sessionListContainer } from './style.css'
import { SessionOverviewComponent } from '../SessionOverview'

type SessionTreeProperties = {
  // sessions may be a flat array of SessionOverview or hierarchical nodes
  currentSessionId: string | null
  sessions: SessionOverview[] | SessionTreeNodeType[]
  handleSelectSession: (sessionId: string) => Promise<void>
  onRefresh: () => Promise<void>
}

export const SessionTree = ({
  currentSessionId,
  sessions,
  handleSelectSession,
  onRefresh
}: SessionTreeProperties): JSX.Element => {
  const {
    sessionReferences,
    handleAnchorClick,
    handleNewChatClick,
    setSessionReference
  }: UseSessionTreeHandlersReturn = useSessionTreeHandlers(onRefresh)

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
                  handleSelectSession={handleSelectSession}
                  ref={setSessionReference(session.sessionId)}
                />
              )
            })}
      </ul>
      <SessionTreeFooter handleNewChatClick={handleNewChatClick} />
    </div>
  )
}
