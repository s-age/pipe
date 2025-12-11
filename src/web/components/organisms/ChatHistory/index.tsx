import type { JSX } from 'react'
import { useParams } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { ChatHistoryBody } from './ChatHistoryBody'
import { ChatHistoryFooter } from './ChatHistoryFooter'
import { ChatHistoryHeader } from './ChatHistoryHeader'
import { useChatHistoryActions } from './hooks/useChatHistoryActions'
import { useChatHistoryHandlers } from './hooks/useChatHistoryHandlers'
import { useChatStreaming } from './hooks/useChatStreaming'
import { chatRoot } from './style.css'

type ChatHistoryProperties = {
  sessionDetail: SessionDetail | null
  expertMode: boolean
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

// Keep a default export for backward compatibility (renders the full composed view)
export const ChatHistory = ({
  sessionDetail,
  expertMode,
  setSessionDetail,
  refreshSessionsInStore
}: ChatHistoryProperties): JSX.Element => {
  const parameters = useParams()
  const sessionId = parameters['*'] || null

  const {
    streamingTurns,
    isStreaming,
    turnsListReference,
    onSendInstruction,
    scrollToBottom
  } = useChatStreaming({
    currentSessionId: sessionId,
    // ChatHistory hook expects a loose setter type; cast to unknown to satisfy lint
    setSessionDetail: setSessionDetail
  })

  const { handleDeleteCurrentSession } = useChatHistoryHandlers({
    currentSessionId: sessionId,
    refreshSessionsInStore
  })

  const { refreshSession } = useChatHistoryActions({
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
        onRefresh={refreshSession}
        refreshSessionsInStore={refreshSessionsInStore}
        scrollToBottom={scrollToBottom}
      />
      <ChatHistoryFooter
        currentSessionId={sessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
        tokenCount={tokenCount}
        contextLimit={contextLimit}
        onRefresh={refreshSession}
      />
    </div>
  )
}
