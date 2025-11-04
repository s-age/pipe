import { JSX, useCallback, useState } from 'react'

import SessionList from '@/components/organisms/SessionList'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import TurnsList from '@/components/organisms/TurnsList'
import { getSession } from '@/lib/api/session/getSession'

import { appContainer } from './style.css'
import { useSessionActions } from './useSessionActions'
import { useSessionManagement } from './useSessionManagement'
import { useStreamingInstruction } from './useStreamingInstruction'

const HomePage = (): JSX.Element => {
  const {
    sessions,
    currentSessionId,
    sessionData,
    error,
    handleSessionSelect,
    handleMetaSave,
    handleDeleteSession,
    setSessionData,
  } = useSessionManagement()

  const setError = useState<string | null>(null)[1]

  const loadSessionDataAfterStreaming = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      try {
        const data = await getSession(currentSessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        console.error('Failed to load session data after streaming:', err)
      }
    }
  }, [currentSessionId, setSessionData])

  const {
    streamedText,
    isStreaming,
    streamingError,
    handleSendInstruction,
    setStreamingTrigger,
  } = useStreamingInstruction(
    currentSessionId,
    setSessionData,
    loadSessionDataAfterStreaming,
  )

  const {
    handleDeleteTurn,
    handleForkSession,
    handleUpdateTodo,
    handleDeleteAllTodos,
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  } = useSessionActions(sessionData, setSessionData)

  // ストリーミングエラーをHomePageのerror状態に反映
  if (streamingError) {
    setError(streamingError)
    setStreamingTrigger(null)
  }

  const expertMode = true // 仮の値

  if (error) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {error}
      </div>
    )
  }

  return (
    <div className={appContainer}>
      <SessionList
        sessions={sessions}
        currentSessionId={currentSessionId}
        handleSessionSelect={handleSessionSelect}
      />
      <TurnsList
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        onDeleteTurn={handleDeleteTurn}
        onForkSession={handleForkSession}
        onSendInstruction={handleSendInstruction}
        onDeleteSession={handleDeleteSession}
        streamedText={streamedText}
        isStreaming={isStreaming}
      />
      <SessionMeta
        key={currentSessionId}
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        onUpdateTodo={handleUpdateTodo}
        onDeleteAllTodos={handleDeleteAllTodos}
        onUpdateReferencePersist={handleUpdateReferencePersist}
        onUpdateReferenceTtl={handleUpdateReferenceTtl}
        onUpdateReferenceDisabled={handleUpdateReferenceDisabled}
      />
    </div>
  )
}

export default HomePage
