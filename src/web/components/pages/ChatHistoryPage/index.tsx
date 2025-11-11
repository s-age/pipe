import type { JSX } from 'react'

import { ChatHistory } from '@/components/organisms/ChatHistory'
import { Header } from '@/components/organisms/Header'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import { SessionTree } from '@/components/organisms/SessionTree'

import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'
import {
  appContainer,
  mainContent,
  leftColumn,
  centerColumn,
  rightColumn
} from './style.css'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    sessions,
    currentSessionId,
    sessionDetail,
    roleOptions,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh
  } = useChatHistoryPageHandlers()

  return (
    <div className={appContainer}>
      <Header />
      <div className={mainContent}>
        <div className={leftColumn}>
          <SessionTree
            sessions={sessions}
            currentSessionId={currentSessionId}
            selectSession={selectSession}
          />
        </div>

        <div className={centerColumn}>
          <ChatHistory
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            expertMode={expertMode}
            setSessionDetail={setSessionDetail}
          />
        </div>

        <div className={rightColumn}>
          <SessionMeta
            key={currentSessionId}
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            onRefresh={onRefresh}
            roleOptions={roleOptions}
          />
        </div>
      </div>
    </div>
  )
}

// Default export removed — use named export `ChatHistoryPage`
