import type { JSX } from 'react'

import {
  ChatHistoryHeader,
  ChatHistoryList,
  ChatHistoryFooter,
} from '@/components/organisms/ChatHistory'
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
  panelBottomSpacing,
  errorMessage as errorMessageStyle,
} from './style.css'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    errorMessage,
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    setError,
    refreshSessions,
    actions,
  } = useChatHistoryPageLogic()

  const {
    streamedText,
    isStreaming,
    turnsListReference,
    handleDeleteTurn,
    handleForkSession,
    handleDeleteCurrentSession,
    onSendInstruction,
  } = useChatHistoryLogic({
    currentSessionId,
    setSessionDetail: setSessionDetail as unknown as (data: unknown) => void,
    setError,
    refreshSessions,
  })

  if (errorMessage) {
    return (
      <div className={appContainer}>
        <div className={errorMessageStyle}>Error: {errorMessage}</div>
      </div>
    )
  }

  return (
    <div className={appContainer}>
      <Header />
      <div className={mainContent}>
        <div className={leftColumn}>
          <SessionTree
            sessions={sessions}
            currentSessionId={currentSessionId}
            selectSession={selectSession}
            setError={setError}
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
              handleDeleteTurn={handleDeleteTurn}
              handleForkSession={handleForkSession}
            />
          </div>

          {/* Footer / new-instruction sits below the panel */}
          <ChatHistoryFooter
            currentSessionId={currentSessionId}
            onSendInstruction={onSendInstruction}
            refreshSessions={refreshSessions}
            setError={setError}
            isStreaming={isStreaming}
          />
        </div>

        <div className={rightColumn}>
          <SessionMeta
            key={currentSessionId}
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            setError={setError}
            refreshSessions={refreshSessions}
            actions={actions}
          />
        </div>
      </div>
    </div>
  )
}

// Default export removed — use named export `ChatHistoryPage`
