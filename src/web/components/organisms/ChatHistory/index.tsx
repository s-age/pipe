import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { ChatHistoryBody } from './ChatHistoryBody'
import { ChatHistoryFooter } from './ChatHistoryFooter'
import { ChatHistoryHeader } from './ChatHistoryHeader'
import { useChatHistoryHandlers } from './hooks/useChatHistoryHandlers'
import { useChatHistoryLogic } from './hooks/useChatHistoryLogic'
import { chatRoot } from './style.css'

type ChatHistoryProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  expertMode: boolean
  setSessionDetail: (data: SessionDetail | null) => void
  onRefresh: () => Promise<void>
}

// Keep a default export for backward compatibility (renders the full composed view)
export const ChatHistory = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  setSessionDetail,
  onRefresh
}: ChatHistoryProperties): JSX.Element => {
  const { handleDeleteCurrentSession } = useChatHistoryHandlers({
    currentSessionId
  })

  const { streamedText, isStreaming, turnsListReference, onSendInstruction } =
    useChatHistoryLogic({
      currentSessionId,
      // ChatHistory hook expects a loose setter type; cast to unknown to satisfy lint
      setSessionDetail: setSessionDetail as unknown as (data: unknown) => void
    })
  // scrolling handled in useChatHistoryLogic

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
        onRefresh={onRefresh}
      />
      <ChatHistoryFooter
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
      />
    </div>
  )
}
