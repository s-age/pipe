import { JSX } from 'react'

import ChatHistory from '@/components/organisms/ChatHistory'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'

import { appContainer } from './style.css'
import { useChatHistoryPageLogic } from './useChatHistoryPageLogic.ts'

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
    handleMetaSave,
  } = useChatHistoryPageLogic()

  if (errorMessage) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {errorMessage}
      </div>
    )
  }

  return (
    <div className={appContainer}>
      <SessionTree
        sessions={sessions}
        currentSessionId={currentSessionId}
        selectSession={selectSession}
        setError={setError}
      />
      <ChatHistory
        currentSessionId={currentSessionId}
        sessionDetail={sessionDetail}
        expertMode={expertMode}
        setSessionDetail={setSessionDetail}
        setError={setError}
        refreshSessions={refreshSessions}
      />
      <SessionMeta
        key={currentSessionId}
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        setSessionDetail={setSessionDetail}
        setError={setError}
        refreshSessions={refreshSessions}
      />
    </div>
  )
}

export default ChatHistoryPage
