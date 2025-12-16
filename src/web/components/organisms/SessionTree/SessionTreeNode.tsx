import clsx from 'clsx'
import type { JSX } from 'react'

import type {
  SessionOverview,
  SessionTreeNode as SessionTreeNodeType
} from '@/lib/api/sessionTree/getSessionTree'

import {
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

type SessionTreeNodeProperties = {
  node: SessionTreeNodeType
  depth?: number
  currentSessionId: string | null
  handleAnchorClick: (event: React.MouseEvent<HTMLAnchorElement>) => void
  setSessionReference: (sessionId: string) => (element: HTMLLIElement | null) => void
}

export const SessionTreeNode = ({
  node,
  depth = 0,
  currentSessionId,
  handleAnchorClick,
  setSessionReference
}: SessionTreeNodeProperties): JSX.Element => {
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

  const overview = node.overview || {}
  const sessionObject: SessionOverview = {
    sessionId: node.sessionId,
    purpose: (overview.purpose as string) || '',
    background: (overview.background as string) || '',
    roles: (overview.roles as string[]) || [],
    procedure: (overview.procedure as string) || '',
    artifacts: (overview.artifacts as string[]) || [],
    multiStepReasoningEnabled: !!overview.multiStepReasoningEnabled,
    tokenCount: (overview.tokenCount as number) || 0,
    lastUpdatedAt: (overview.lastUpdatedAt as string) || ''
  }

  const depthClass = depthClasses[depth] ?? depthClasses[0]

  const getShortHash = (sessionId: string): string => {
    const parts = sessionId.split('/')

    return parts[parts.length - 1]?.substring(0, 8) || sessionId.substring(0, 8)
  }

  return (
    <li
      key={node.sessionId}
      className={`${sessionListItem} ${depthClass}`}
      ref={setSessionReference(node.sessionId)}
    >
      <a
        href={`/session/${node.sessionId}`}
        data-session-id={node.sessionId}
        className={clsx(sessionLink, {
          [sessionLinkActive]: node.sessionId === currentSessionId
        })}
        onClick={handleAnchorClick}
      >
        {sessionObject.purpose}{' '}
        <p className={sessionIdStyle}>{getShortHash(node.sessionId)}</p>
      </a>
      {node.children && node.children.length > 0 && (
        <ul className={nestedList}>
          {node.children.map((child) => (
            <SessionTreeNode
              key={child.sessionId}
              node={child}
              depth={depth + 1}
              currentSessionId={currentSessionId}
              handleAnchorClick={handleAnchorClick}
              setSessionReference={setSessionReference}
            />
          ))}
        </ul>
      )}
    </li>
  )
}
