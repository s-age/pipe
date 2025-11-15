import type { JSX } from 'react'

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
  currentSessionId: string | null
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
  currentSessionId,
  expertMode,
  setSessionDetail,
  refreshSessionsInStore
}: ChatHistoryProperties): JSX.Element => {
  const { streamedText, isStreaming, turnsListReference, onSendInstruction } =
    useChatStreaming({
      currentSessionId,
      // ChatHistory hook expects a loose setter type; cast to unknown to satisfy lint
      setSessionDetail: setSessionDetail
    })

  const { handleDeleteCurrentSession } = useChatHistoryHandlers({
    currentSessionId,
    refreshSessionsInStore
  })

  const { refreshSession } = useChatHistoryActions({
    currentSessionId,
    refreshSessionsInStore
  })

  return (
    <div className={chatRoot}>
      <ChatHistoryHeader
        sessionDetail={sessionDetail}
        handleDeleteCurrentSession={handleDeleteCurrentSession}
      />
      <ChatHistoryBody
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        isStreaming={isStreaming}
        streamedText={streamedText}
        turnsListReference={turnsListReference}
        onRefresh={refreshSession}
        refreshSessionsInStore={refreshSessionsInStore}
      />
      <ChatHistoryFooter
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
      />
    </div>
  )
}
