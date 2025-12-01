import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Header } from '@/components/organisms/Header'
import { SessionList } from '@/components/organisms/SessionList'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useSessionManagementActions } from './hooks/useSessionManagementActions'
import { useSessionManagementHandlers } from './hooks/useSessionManagementHandlers'
import { useSessionManagementLifecycle } from './hooks/useSessionManagementLifecycle'
import {
  appContainer,
  mainContent,
  sessionManagementContainer,
  headerSection,
  title,
  actionsSection
} from './style.css'

export const SessionManagementPage: React.FC = () => {
  const { state, actions: storeActions } = useSessionStore()
  const actions = useSessionManagementActions()
  const handlers = useSessionManagementHandlers({ actions })
  useSessionManagementLifecycle({ storeActions })

  const { selectedSessionIds, handleSelectAll, handleSelectSession, handleBulkDelete } =
    handlers

  return (
    <div className={appContainer}>
      <Header />
      <div className={mainContent}>
        <div className={sessionManagementContainer}>
          <div className={headerSection}>
            <Heading level={1} className={title}>
              Session Management
            </Heading>
            <div className={actionsSection}>
              <Button
                onClick={handleBulkDelete}
                disabled={selectedSessionIds.length === 0}
              >
                Bulk Delete Selected Sessions
              </Button>
            </div>
          </div>
          <SessionList
            sessions={state.sessionTree.sessions}
            selectedSessionIds={selectedSessionIds}
            onSelectAll={handleSelectAll}
            onSelectSession={handleSelectSession}
          />
        </div>
      </div>
    </div>
  )
}
