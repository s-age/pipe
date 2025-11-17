import type { JSX } from 'react'
import { useRef } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionTreeHandlers } from './hooks/useSessionTreeHandlers'
import { useSessionTreeLifecycle } from './hooks/useSessionTreeLifecycle'
import { SessionTreeFooter } from './SessionTreeFooter'
import {
  sessionListColumn,
  sessionListContainer,
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle,
  nestedList,
  depth0,
  depth1,
  depth2,
  depth3,
  depth4,
  depth5,
  depth6,
  depth7,
  depth8,
  depth9,
  depth10
} from './style.css'
import { SessionOverviewComponent } from '../SessionOverview'

type SessionTreeProperties = {
  // sessions may be a flat array of SessionOverview or hierarchical nodes
  sessions: SessionOverview[] | SessionTreeNode[]
  currentSessionId: string | null
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}

export const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession
}: SessionTreeProperties): JSX.Element => {
  const sessionReferences = useRef<Map<string, HTMLLIElement>>(new Map())
  const { handleNewChatClick, handleAnchorClick, setSessionReference } =
    useSessionTreeHandlers(selectSession, sessionReferences)

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
        'overview' in (sessions[0] as SessionOverview | SessionTreeNode)
          ? // hierarchical nodes: render recursively
            (sessions as SessionTreeNode[]).map((node: SessionTreeNode) => {
              const depthClasses = [
                depth0,
                depth1,
                depth2,
                depth3,
                depth4,
                depth5,
                depth6,
                depth7,
                depth8,
                depth9,
                depth10
              ]

              const renderNode = (n: SessionTreeNode, depth = 0): JSX.Element => {
                const overview = n.overview || {}
                const sessionObject: SessionOverview = {
                  session_id: n.session_id,
                  purpose: (overview.purpose as string) || '',
                  background: (overview.background as string) || '',
                  roles: (overview.roles as string[]) || [],
                  procedure: (overview.procedure as string) || '',
                  artifacts: (overview.artifacts as string[]) || [],
                  multi_step_reasoning_enabled: !!overview.multi_step_reasoning_enabled,
                  token_count: (overview.token_count as number) || 0,
                  last_update: (overview.last_update as string) || ''
                }

                const depthClass = depthClasses[depth] ?? depthClasses[0]

                let childrenElements: JSX.Element[] | null = null

                if (n.children && n.children.length > 0) {
                  childrenElements = n.children.map((child: SessionTreeNode) =>
                    renderNode(child, depth + 1)
                  )
                }

                return (
                  <li
                    key={n.session_id}
                    className={`${sessionListItem} ${depthClass}`}
                    ref={setSessionReference(n.session_id)}
                  >
                    <a
                      href={`/session/${n.session_id}`}
                      data-session-id={n.session_id}
                      className={`${sessionLink} ${n.session_id === currentSessionId ? sessionLinkActive : ''}`.trim()}
                      onClick={handleAnchorClick}
                    >
                      {sessionObject.purpose}{' '}
                      <p className={sessionIdStyle}>
                        {String(sessionObject.session_id).substring(0, 8)}
                      </p>
                    </a>
                    {childrenElements && (
                      <ul className={nestedList}>{childrenElements}</ul>
                    )}
                  </li>
                )
              }

              return renderNode(node)
            })
          : // flat list: render as before
            (sessions as SessionOverview[]).map((session) => {
              if (!session.session_id || typeof session.session_id !== 'string') {
                console.warn('Skipping session with invalid session_id:', session)

                return null // Invalid session, skip rendering
              }

              return (
                <SessionOverviewComponent
                  key={session.session_id}
                  session={session}
                  currentSessionId={currentSessionId || ''}
                  selectSession={selectSession}
                  ref={setSessionReference(session.session_id)}
                />
              )
            })}
      </ul>
      <SessionTreeFooter handleNewChatClick={handleNewChatClick} />
    </div>
  )
}
