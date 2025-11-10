import React, { useEffect, useRef, useCallback } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { useModal } from '@/components/molecules/Modal/hooks/useModal'
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
  // refreshSessions: (sessionDetail: SessionDetail, sessions?: SessionOverview[]) => void // Removed as onRefresh handles this
}

type ChatHistoryLogicReturn = {
  streamedText: string | null
  isStreaming: boolean
  turnsListReference: React.RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  handleDeleteCurrentSession: () => void
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
  handleDeleteSession: (sessionId: string) => Promise<void>
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

  const { show, hide } = useModal()

  const modalIdReference = useRef<number | null>(null)

  const handleDeleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      // This is a placeholder for the actual delete session API call
      console.log(`Deleting session ${sessionId}`)
      // After deleting the session, we need to refresh the session tree
      // and potentially clear the current session detail if the deleted session was the current one.
      // For now, we'll just call the onRefresh to update the session tree.
      await onRefresh()
    },
    [onRefresh]
  )

  const handleDeleteCurrentSession = useCallback((): void => {
    if (!currentSessionId) return

    const sessionIdAtShow = currentSessionId

    const handleConfirm = (): void => {
      void handleDeleteSession(sessionIdAtShow)
      if (modalIdReference.current !== null) {
        hide(modalIdReference.current)
        modalIdReference.current = null
      }
    }

    const handleCancel = (): void => {
      if (modalIdReference.current !== null) {
        hide(modalIdReference.current)
        modalIdReference.current = null
      }
    }

    modalIdReference.current = show(
      React.createElement(ConfirmModal, {
        title: 'Delete Session',
        message:
          'Are you sure you want to delete this session? This action cannot be undone.',
        onConfirm: handleConfirm,
        onCancel: handleCancel,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })
    )
  }, [currentSessionId, handleDeleteSession, hide, show])

  return {
    streamedText,
    isStreaming,
    turnsListReference,
    scrollToBottom,
    handleDeleteCurrentSession,
    deleteTurnAction,
    forkSessionAction,
    handleDeleteSession,
    onSendInstruction
  }
}

export type { ChatHistoryLogicReturn, ChatHistoryProperties }
