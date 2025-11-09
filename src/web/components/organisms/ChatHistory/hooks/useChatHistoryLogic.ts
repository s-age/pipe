import { useEffect, useRef, useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { useStreamingInstruction } from '@/components/pages/ChatHistoryPage/hooks/useStreamingInstruction'

import { useTurnActions } from './useTurnActions'

type ChatHistoryProperties = {
  currentSessionId: string | null
  // keep the setter type loose here to avoid import-order lint churn
  setSessionDetail: (data: unknown) => void
  refreshSessions: () => Promise<void>
}

type ChatHistoryLogicReturn = {
  streamedText: string | null
  isStreaming: boolean
  turnsListReference: React.RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  handleDeleteCurrentSession: () => void
  handleDeleteTurn: (sessionId: string, turnIndex: number) => Promise<void>
  handleForkSession: (sessionId: string, forkIndex: number) => Promise<void>
  handleDeleteSession: (sessionId: string) => Promise<void>
  onSendInstruction: (instruction: string) => Promise<void>
}

export const useChatHistoryLogic = ({
  currentSessionId,
  setSessionDetail,
  refreshSessions,
}: ChatHistoryProperties): ChatHistoryLogicReturn => {
  const {
    streamedText,
    isStreaming,
    streamingError,
    onSendInstruction,
    setStreamingTrigger,
  } = useStreamingInstruction(currentSessionId, setSessionDetail)

  const { handleDeleteTurn, handleForkSession, handleDeleteSession } =
    useTurnActions(refreshSessions)
  const toast = useToast()

  // propagate streaming errors
  useEffect(() => {
    if (streamingError) {
      toast.failure(streamingError)
      setStreamingTrigger(null)
    }
  }, [streamingError, setStreamingTrigger, toast])

  const turnsListReference = useRef<HTMLDivElement | null>(null)

  const scrollToBottom = useCallback((): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }, [])

  // auto-scroll when streaming text appears or when session changes
  useEffect(() => {
    scrollToBottom()
  }, [streamedText, currentSessionId, scrollToBottom])

  const handleDeleteCurrentSession = useCallback((): void => {
    if (currentSessionId) void handleDeleteSession(currentSessionId)
  }, [currentSessionId, handleDeleteSession])

  return {
    streamedText,
    isStreaming,
    turnsListReference,
    scrollToBottom,
    handleDeleteCurrentSession,
    handleDeleteTurn,
    handleForkSession,
    handleDeleteSession,
    onSendInstruction,
  }
}

export type { ChatHistoryLogicReturn, ChatHistoryProperties }
