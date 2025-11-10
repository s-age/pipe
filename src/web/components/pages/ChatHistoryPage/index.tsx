import type { JSX } from 'react'

import {
  ChatHistoryHeader,
  ChatHistoryList,
  ChatHistoryFooter
} from '@/components/organisms/ChatHistory'
import { useChatHistoryHandlers } from '@/components/organisms/ChatHistory/hooks/useChatHistoryHandlers'
import { useChatHistoryLogic } from '@/components/organisms/ChatHistory/hooks/useChatHistoryLogic'
import { Header } from '@/components/organisms/Header'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import { SessionTree } from '@/components/organisms/SessionTree'

import { useChatHistoryPageLogic } from './hooks/useChatHistoryPageLogic.ts'
import {
  appContainer,
  mainContent,
  leftColumn,
  centerColumn,
  rightColumn,
  panel,
  panelBottomSpacing
} from './style.css'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh
  } = useChatHistoryPageLogic()

  const { handleDeleteCurrentSession } = useChatHistoryHandlers({
    currentSessionId
  })

  const { streamedText, isStreaming, turnsListReference, onSendInstruction } =
    useChatHistoryLogic({
      currentSessionId,
      setSessionDetail: setSessionDetail as unknown as (data: unknown) => void
    })

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
          {/* Header sits above the boxed panel */}
          <ChatHistoryHeader
            sessionDetail={sessionDetail}
            handleDeleteCurrentSession={handleDeleteCurrentSession}
          />

          <div className={`${panel} ${panelBottomSpacing}`}>
            {/* Panel contains only the turns list */}
            <ChatHistoryList
              sessionDetail={sessionDetail}
              currentSessionId={currentSessionId}
              expertMode={expertMode}
              isStreaming={isStreaming}
              streamedText={streamedText}
              turnsListReference={turnsListReference}
              onRefresh={onRefresh}
            />
          </div>

          {/* Footer / new-instruction sits below the panel */}
          <ChatHistoryFooter
            currentSessionId={currentSessionId}
            onSendInstruction={onSendInstruction}
            isStreaming={isStreaming}
          />
        </div>

        <div className={rightColumn}>
          <SessionMeta
            key={currentSessionId}
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            onRefresh={onRefresh}
          />
        </div>
      </div>
    </div>
  )
}

// Default export removed — use named export `ChatHistoryPage`
