import React, { type JSX } from 'react'

import { Checkbox } from '@/components/atoms/Checkbox'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Grid } from '@/components/molecules/Grid'
import { SessionItem } from '@/components/molecules/SessionItem'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionListHandlers } from './hooks/useSessionListHandlers'
import { useSessionListLifecycle } from './hooks/useSessionListLifecycle'
import { SessionListNode } from './SessionListNode'
import {
  sessionList,
  header,
  headerLabel,
  headerCheckbox,
  headerSubject,
  headerShortHash,
  headerUpdatedAt
} from './style.css'

type Properties = {
  selectedSessionIds: string[]
  sessions: SessionOverview[] | SessionTreeNode[]
  updateLabel?: string
  useFilePath?: boolean
  onSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
  onSelectSession: (sessionId: string, isSelected: boolean) => void
}

export const SessionList = ({
  selectedSessionIds,
  sessions,
  updateLabel = 'Updated At',
  useFilePath = false,
  onSelectAll,
  onSelectSession
}: Properties): JSX.Element => {
  const getAllSessionIds = (
    sessions: SessionOverview[] | SessionTreeNode[]
  ): string[] => {
    const ids: string[] = []
    const collectIds = (items: SessionOverview[] | SessionTreeNode[]): void => {
      items.forEach((item) => {
        // For archives with filePath, use filePath as unique identifier
        if (useFilePath && 'filePath' in item && item.filePath) {
          ids.push(item.filePath)
        } else if ('overview' in item) {
          // For tree nodes, use sessionId
          ids.push(item.sessionId)
        } else {
          // For flat sessions, use sessionId
          ids.push(item.sessionId)
        }
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

      return treeNodes.map((node) => (
        <SessionListNode
          key={node.sessionId}
          node={node}
          selectedSessionIds={selectedSessionIds}
          onSelectSession={onSelectSession}
          updateLabel={updateLabel}
        />
      ))
    } else {
      // Flat list: render as before
      const flatSessions = sessions as SessionOverview[]

      return flatSessions.map((session) => {
        const itemId =
          useFilePath && session.filePath ? session.filePath : session.sessionId

        return (
          <SessionItem
            key={itemId}
            session={session}
            isSelected={selectedSessionIds.includes(itemId)}
            onSelect={onSelectSession}
            updateLabel={updateLabel}
            useFilePath={useFilePath}
          />
        )
      })
    }
  }

  return (
    <FlexColumn className={sessionList}>
      <Flex className={header} align="center">
        <Flex as="label" className={headerLabel} align="center">
          <Checkbox
            ref={checkboxRef}
            id="select-all-sessions"
            className={headerCheckbox}
            checked={allSelected}
            onChange={handleSelectAll}
          />
          <Grid columns="1fr 100px 180px" gap="s">
            <span className={headerSubject}>Subject</span>
            <span className={headerShortHash}>Short Hash</span>
            <span className={headerUpdatedAt}>{updateLabel}</span>
          </Grid>
        </Flex>
      </Flex>
      {renderSessions()}
    </FlexColumn>
  )
}
