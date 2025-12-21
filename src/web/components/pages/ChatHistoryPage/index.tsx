import type { JSX } from 'react'

import { AppLayout } from '@/components/layouts/AppLayout'
import { ChatHistory } from '@/components/organisms/ChatHistory'
import { SessionControl } from '@/components/organisms/SessionControl'
import { SessionTree } from '@/components/organisms/SessionTree'

import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'
import { mainContent, leftColumn, centerColumn } from './style.css.ts'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    sessions,
    sessionDetail,
    expertMode,
    handleSelectSession,
    setSessionDetail,
    onRefresh,
    refreshSessionsInStore
  } = useChatHistoryPageHandlers()

  return (
    <AppLayout>
      <div className={mainContent}>
        <div className={leftColumn}>
          <SessionTree
            currentSessionId={sessionDetail?.sessionId ?? null}
            sessions={sessions}
            handleSelectSession={handleSelectSession}
            onRefresh={onRefresh}
          />
        </div>

        <div className={centerColumn}>
          <ChatHistory
            sessionDetail={sessionDetail}
            expertMode={expertMode}
            setSessionDetail={setSessionDetail}
            refreshSessionsInStore={refreshSessionsInStore}
          />
        </div>

        {sessionDetail && (
          <SessionControl
            sessionDetail={sessionDetail}
            onRefresh={onRefresh}
            onSessionDetailUpdate={setSessionDetail}
          />
        )}
      </div>
    </AppLayout>
  )
}
