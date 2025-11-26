import type { JSX } from 'react'

import { ChatHistory } from '@/components/organisms/ChatHistory'
import { Header } from '@/components/organisms/Header'
import { SessionControl } from '@/components/organisms/SessionControl'
import { SessionTree } from '@/components/organisms/SessionTree'

import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'
import { appContainer, mainContent, leftColumn, centerColumn } from './style.css'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    sessions,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh,
    refreshSessionsInStore
  } = useChatHistoryPageHandlers()

  return (
    <div className={appContainer}>
      <Header />
      <div className={mainContent}>
        <div className={leftColumn}>
          <SessionTree
            currentSessionId={sessionDetail?.session_id ?? null}
            sessions={sessions}
            selectSession={selectSession}
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
          <SessionControl sessionDetail={sessionDetail} onRefresh={onRefresh} />
        )}
      </div>
    </div>
  )
}
