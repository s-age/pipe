import { useEffect, useRef, useCallback, type RefObject } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { useStreamingInstruction } from '@/components/pages/ChatHistoryPage/hooks/useStreamingInstruction'
import { getSession } from '@/lib/api/session/getSession'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useTurnActions } from './useTurnActions'

type ChatHistoryProperties = {
  currentSessionId: string | null
  // keep the setter type loose here to avoid import-order lint churn
  setSessionDetail: (data: unknown) => void
}

type ChatHistoryLogicReturn = {
  streamedText: string | null
  isStreaming: boolean
  turnsListReference: RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
  onSendInstruction: (instruction: string) => Promise<void>
}

export const useChatHistoryLogic = ({
  currentSessionId,
  setSessionDetail
}: ChatHistoryProperties): ChatHistoryLogicReturn => {
  const {
    streamedText,
    isStreaming,
    streamingError,
    onSendInstruction,
    setStreamingTrigger
  } = useStreamingInstruction(currentSessionId, setSessionDetail)

  const { actions } = useSessionStore()
  const { refreshSessions: refreshSessionsInStore } = actions

  const onRefresh = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      const fetchedSessionDetailResponse = await getSession(currentSessionId)
      const fetchedSessionTree = await getSessionTree()
      const newSessions = fetchedSessionTree.sessions.map(([id, session]) => ({
        ...session,
        session_id: id
      }))
      refreshSessionsInStore(fetchedSessionDetailResponse.session, newSessions)
    }
  }, [currentSessionId, refreshSessionsInStore])

  const { deleteTurnAction, forkSessionAction } = useTurnActions(onRefresh)
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

  // Deletion handlers moved to useChatHistoryHandlers to keep this hook
  // focused on streaming and turn-level actions.

  return {
    streamedText,
    isStreaming,
    turnsListReference,
    scrollToBottom,
    deleteTurnAction,
    forkSessionAction,
    onSendInstruction
  }
}

export type { ChatHistoryLogicReturn, ChatHistoryProperties }
