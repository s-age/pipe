import React from 'react'

import { Checkbox } from '@/components/atoms/Checkbox'
import { SessionItem } from '@/components/molecules/SessionItem'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionListHandlers } from './hooks/useSessionListHandlers'
import { useSessionListLifecycle } from './hooks/useSessionListLifecycle'
import {
  sessionList,
  header,
  headerCheckbox,
  headerName,
  headerCreatedAt,
  sessionNode,
  sessionChildren
} from './style.css'

type Properties = {
  sessions: SessionOverview[] | SessionTreeNode[]
  selectedSessionIds: string[]
  onSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  onSelectSession: (sessionId: string, isSelected: boolean) => void
}

export const SessionList: React.FC<Properties> = ({
  sessions,
  selectedSessionIds,
  onSelectAll,
  onSelectSession
}) => {
  const getAllSessionIds = (
    sessions: SessionOverview[] | SessionTreeNode[]
  ): string[] => {
    const ids: string[] = []
    const collectIds = (items: SessionOverview[] | SessionTreeNode[]): void => {
      items.forEach((item) => {
        ids.push(item.session_id)
        if ('children' in item && item.children) {
          collectIds(item.children)
        }
      })
    }
    collectIds(sessions)

    return ids
  }

  const allSessionIds = getAllSessionIds(sessions)
  const allSelected =
    allSessionIds.length > 0 && selectedSessionIds.length === allSessionIds.length
  const someSelected =
    selectedSessionIds.length > 0 && selectedSessionIds.length < allSessionIds.length

  const { checkboxRef } = useSessionListLifecycle(allSelected, someSelected)
  const { handleSelectAll } = useSessionListHandlers(sessions, allSelected, onSelectAll)

  const renderSessions = (): React.ReactNode | null => {
    if (!Array.isArray(sessions) || sessions.length === 0) return null

    // Check if it's hierarchical (SessionTreeNode[])
    if ('overview' in sessions[0]) {
      // Hierarchical nodes: render recursively
      const treeNodes = sessions as SessionTreeNode[]

      return treeNodes.map((node) => renderNode(node))
    } else {
      // Flat list: render as before
      const flatSessions = sessions as SessionOverview[]

      return flatSessions.map((session) => (
        <SessionItem
          key={session.session_id}
          session={session}
          isSelected={selectedSessionIds.includes(session.session_id)}
          onSelect={onSelectSession}
        />
      ))
    }
  }

  const renderNode = (node: SessionTreeNode): React.ReactElement => {
    const overview = node.overview || {}
    const sessionObject: SessionOverview = {
      session_id: node.session_id,
      purpose: (overview.purpose as string) || '',
      background: (overview.background as string) || '',
      roles: (overview.roles as string[]) || [],
      procedure: (overview.procedure as string) || '',
      artifacts: (overview.artifacts as string[]) || [],
      multi_step_reasoning_enabled: !!overview.multi_step_reasoning_enabled,
      token_count: (overview.token_count as number) || 0,
      last_update: (overview.last_updated as string) || ''
    }

    let childrenElements: React.ReactElement[] | null = null
    if (node.children && node.children.length > 0) {
      childrenElements = node.children.map((child) => renderNode(child))
    }

    return (
      <div key={node.session_id} className={sessionNode}>
        <SessionItem
          session={sessionObject}
          isSelected={selectedSessionIds.includes(node.session_id)}
          onSelect={onSelectSession}
        />
        {childrenElements && <div className={sessionChildren}>{childrenElements}</div>}
      </div>
    )
  }

  return (
    <div className={sessionList}>
      <div className={header}>
        <Checkbox
          ref={checkboxRef}
          className={headerCheckbox}
          checked={allSelected}
          onChange={handleSelectAll}
        />
        <span className={headerName}>Session Name</span>
        <span className={headerCreatedAt}>Created At</span>
      </div>
      {renderSessions()}
    </div>
  )
}
