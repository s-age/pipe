import { JSX } from 'react'

import ChatHistory from '@/components/organisms/ChatHistory'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'
import useSessionStore from '@/stores/useChatHistoryStore'

import { appContainer } from './style.css'
import { useSessionDetailLoader } from './useSessionDetailLoader'
import { useSessionLoader } from './useSessionLoader'
import { useSessionMetaSaver } from './useSessionMetaSaver'

const ChatHistoryPage = (): JSX.Element => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    error,
  } = state

  const { selectSession, setSessionDetail, setError, refreshSessions } = actions

  useSessionLoader({ state, actions })
  useSessionDetailLoader({ state, actions })
  const { handleMetaSave } = useSessionMetaSaver({ actions })

  const expertMode = (state.settings.expertMode as boolean) ?? true

  if (error) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {error}
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
