import type { JSX } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Tabs } from '@/components/atoms/Tabs'
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

export const SessionManagementPage = (): JSX.Element => {
  const navigate = useNavigate()
  const { state, actions: storeActions } = useSessionStore()
  const actions = useSessionManagementActions({ storeActions })
  const handlers = useSessionManagementHandlers({ actions, navigate })
  useSessionManagementLifecycle({ storeActions })

  const {
    currentTab,
    setCurrentTab,
    selectedSessionIds,
    handleSelectAll,
    handleSelectSession,
    handleBulkArchive,
    handleBulkDeleteArchived,
    handleCancel
  } = handlers

  const currentSessions =
    currentTab === 'sessions' ? state.sessionTree.sessions : state.archivedSessions
  const currentAction =
    currentTab === 'sessions' ? handleBulkArchive : handleBulkDeleteArchived
  const buttonText =
    currentTab === 'sessions'
      ? 'Bulk Archive Selected Sessions'
      : 'Bulk Delete Archived Sessions'

  const tabs = [
    { key: 'sessions' as const, label: 'Sessions' },
    { key: 'archives' as const, label: 'Archives' }
  ]

  return (
    <AppLayout>
      <div className={pageContent}>
        <div className={scrollableContainer}>
          <Heading level={1}>Session Management</Heading>
          <Tabs tabs={tabs} activeKey={currentTab} onChange={setCurrentTab} />
          <SessionList
            sessions={currentSessions}
            selectedSessionIds={selectedSessionIds}
            onSelectAll={handleSelectAll}
            onSelectSession={handleSelectSession}
            updateLabel={currentTab === 'archives' ? 'Deleted At' : 'Updated At'}
          />
        </div>
        <div className={buttonBar}>
          <Button className={secondaryButton} onClick={handleCancel}>
            Cancel
          </Button>
          <Button
            className={primaryButton}
            onClick={currentAction}
            disabled={selectedSessionIds.length === 0}
          >
            {buttonText}
          </Button>
        </div>
      </div>
    </AppLayout>
  )
}
