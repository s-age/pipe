import { JSX, useCallback } from 'react'

import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'
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
    sessionDetail,
    error,
    handleSessionSelect,
    handleMetaSave,
    handleDeleteSession,
    setSessionDetail,
  } = useSessionManagement()

  const loadSessionDetailAfterStreaming = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      try {
        const data = await getSession(currentSessionId)
        setSessionDetail(data.session)
      } catch (err: unknown) {
        // エラーハンドリングはuseSessionManagementに任せるか、ここでsetErrorを呼ぶ
        console.error('Failed to load session data after streaming:', err)
      }
    }
  }, [currentSessionId, setSessionDetail])

  const {
    streamedText,
    isStreaming,
    streamingError,
    handleSendInstruction,
    setStreamingTrigger,
  } = useStreamingInstruction(currentSessionId, loadSessionDetailAfterStreaming)

  const {
    handleDeleteTurn,
    handleForkSession,
    handleUpdateTodo,
    handleDeleteAllTodos,
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  } = useSessionActions(sessionDetail, setSessionDetail)

  // ストリーミングエラーをHomePageのerror状態に反映
  if (streamingError) {
    // setError(streamingError) // useSessionManagement でエラーを管理するため、ここでは設定しない
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
      <SessionTree
        sessions={sessions}
        currentSessionId={currentSessionId}
        handleSessionSelect={handleSessionSelect}
      />
      <TurnsList
        sessionDetail={sessionDetail}
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
        sessionDetail={sessionDetail}
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
