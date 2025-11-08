import type { JSX } from 'react'

import ChatHistory from '@/components/organisms/ChatHistory'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'

import { useChatHistoryPageLogic } from './hooks/useChatHistoryPageLogic.ts'
import { appContainer } from './style.css'

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
        setSessionDetail={setSessionDetail}
        setError={setError}
        refreshSessions={refreshSessions}
        actions={actions}
      />
    </div>
  )
}

export default ChatHistoryPage
