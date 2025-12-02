import React from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { AppLayout } from '@/components/layouts/AppLayout'
import { SessionList } from '@/components/organisms/SessionList'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionManagementActions } from './hooks/useSessionManagementActions'
import { useSessionManagementHandlers } from './hooks/useSessionManagementHandlers'
import { useSessionManagementLifecycle } from './hooks/useSessionManagementLifecycle'
import {
  pageContent,
  scrollableContainer,
  buttonBar,
  primaryButton,
  secondaryButton
} from './style.css.ts'

export const SessionManagementPage: React.FC = () => {
  const navigate = useNavigate()
  const { state, actions: storeActions } = useSessionStore()
  const actions = useSessionManagementActions()
  const handlers = useSessionManagementHandlers({ actions, navigate })
  useSessionManagementLifecycle({ storeActions })

  const {
    selectedSessionIds,
    handleSelectAll,
    handleSelectSession,
    handleBulkDelete,
    handleCancel
  } = handlers

  return (
    <AppLayout>
      <div className={pageContent}>
        <div className={scrollableContainer}>
          <Heading level={1}>Session Management</Heading>
          <SessionList
            sessions={state.sessionTree.sessions}
            selectedSessionIds={selectedSessionIds}
            onSelectAll={handleSelectAll}
            onSelectSession={handleSelectSession}
          />
        </div>
        <div className={buttonBar}>
          <Button className={secondaryButton} onClick={handleCancel}>
            Cancel
          </Button>
          <Button
            className={primaryButton}
            onClick={handleBulkDelete}
            disabled={selectedSessionIds.length === 0}
          >
            Bulk Delete Selected Sessions
          </Button>
        </div>
      </div>
    </AppLayout>
  )
}
