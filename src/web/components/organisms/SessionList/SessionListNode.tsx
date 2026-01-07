import type { JSX } from 'react'

import { Box } from '@/components/molecules/Box'
import { SessionItem } from '@/components/molecules/SessionItem'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { sessionNode, sessionChildren } from './style.css'

type SessionListNodeProperties = {
  node: SessionTreeNode
  selectedSessionIds: string[]
  updateLabel: string
  onSelectSession: (sessionId: string, isSelected: boolean) => void
}

export const SessionListNode = ({
  node,
  selectedSessionIds,
  updateLabel,
  onSelectSession
}: SessionListNodeProperties): JSX.Element => {
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
    lastUpdatedAt: (overview.lastUpdatedAt as string) || '',
    deletedAt: (overview.deletedAt as string) || ''
  }

  return (
    <Box key={node.sessionId} className={sessionNode}>
      <SessionItem
        session={sessionObject}
        isSelected={selectedSessionIds.includes(node.sessionId)}
        onSelect={onSelectSession}
        updateLabel={updateLabel}
      />
      {node.children && node.children.length > 0 && (
        <Box className={sessionChildren}>
          {node.children.map((child) => (
            <SessionListNode
              key={child.sessionId}
              node={child}
              selectedSessionIds={selectedSessionIds}
              onSelectSession={onSelectSession}
              updateLabel={updateLabel}
            />
          ))}
        </Box>
      )}
    </Box>
  )
}
