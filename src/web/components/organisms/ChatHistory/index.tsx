import type { JSX } from 'react'
import { useParams } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { ChatHistoryBody } from './ChatHistoryBody'
import { ChatHistoryFooter } from './ChatHistoryFooter'
import { ChatHistoryHeader } from './ChatHistoryHeader'
import { useChatHistoryHandlers } from './hooks/useChatHistoryHandlers'
import { useChatStreaming } from './hooks/useChatStreaming'
import { chatRoot } from './style.css'

type ChatHistoryProperties = {
  expertMode: boolean
  sessionDetail: SessionDetail | null
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
  setSessionDetail: (data: SessionDetail | null) => void
}

// Keep a default export for backward compatibility (renders the full composed view)
export const ChatHistory = ({
  expertMode,
  sessionDetail,
  refreshSessionsInStore,
  setSessionDetail
}: ChatHistoryProperties): JSX.Element => {
  const parameters = useParams()
  const sessionId = parameters['*'] || null

  const {
    isStreaming,
    onSendInstruction,
    scrollToBottom,
    streamingTurns,
    turnsListReference
  } = useChatStreaming({
    currentSessionId: sessionId,
    // ChatHistory hook expects a loose setter type; cast to unknown to satisfy lint
    setSessionDetail: setSessionDetail
  })

  const { handleDeleteCurrentSession, handleRefreshSession } = useChatHistoryHandlers({
    currentSessionId: sessionId,
    refreshSessionsInStore
  })

  const tokenCount = sessionDetail?.tokenCount ?? 0
  const contextLimit = sessionDetail?.settings?.contextLimit ?? 700000

  return (
    <div className={chatRoot}>
      <ChatHistoryHeader
        sessionDetail={sessionDetail}
        handleDeleteCurrentSession={handleDeleteCurrentSession}
      />
      <ChatHistoryBody
        sessionDetail={sessionDetail}
        currentSessionId={sessionId ?? null}
        expertMode={expertMode}
        isStreaming={isStreaming}
        streamingTurns={streamingTurns}
        turnsListReference={turnsListReference}
        onRefresh={handleRefreshSession}
        refreshSessionsInStore={refreshSessionsInStore}
        scrollToBottom={scrollToBottom}
      />
      <ChatHistoryFooter
        currentSessionId={sessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
        tokenCount={tokenCount}
        contextLimit={contextLimit}
        onRefresh={handleRefreshSession}
      />
    </div>
  )
}
