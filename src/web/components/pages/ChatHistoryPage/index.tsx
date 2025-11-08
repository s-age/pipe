import type { JSX } from 'react'

import {
  ChatHistoryHeader,
  ChatHistoryList,
  ChatHistoryFooter,
  useChatHistoryLogic,
} from '@/components/organisms/ChatHistory'
import Header from '@/components/organisms/Header'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'

import { useChatHistoryPageLogic } from './hooks/useChatHistoryPageLogic.ts'
import {
  appContainer,
  mainContent,
  leftColumn,
  centerColumn,
  rightColumn,
  panel,
} from './style.css'

const ChatHistoryPage = (): JSX.Element => {
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
    handleDeleteSession,
    onSendInstruction,
  } = useChatHistoryLogic({
    currentSessionId,
    setSessionDetail,
    setError,
    refreshSessions,
  })

  if (errorMessage) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {errorMessage}
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
            currentSessionId={currentSessionId}
            handleDeleteSession={handleDeleteSession}
          />

          <div className={panel} style={{ marginBottom: '8px' }}>
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

export default ChatHistoryPage
