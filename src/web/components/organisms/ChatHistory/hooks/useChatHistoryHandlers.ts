import React, { useCallback, useRef } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { useModal } from '@/components/organisms/ModalManager'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useChatHistoryActions } from './useChatHistoryActions'

type UseChatHistoryHandlersProperties = {
  currentSessionId: string | null
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

export const useChatHistoryHandlers = ({
  currentSessionId,
  refreshSessionsInStore
}: UseChatHistoryHandlersProperties): {
  handleDeleteCurrentSession: () => void
  handleDeleteSession: (sessionId: string) => Promise<void>
  handleRefreshSession: () => Promise<void>
} => {
  const { show, hide } = useModal()
  const { deleteSessionAction, refreshSession } = useChatHistoryActions({
    currentSessionId
  })

  const modalIdReference = useRef<number | null>(null)

  const handleDeleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      // Intentionally not awaiting - errors are handled in Actions layer
      void deleteSessionAction(sessionId)
      location.href = '/'
    },
    [deleteSessionAction]
  )

  const handleRefreshSession = useCallback(async (): Promise<void> => {
    const result = await refreshSession()
    if (result) {
      refreshSessionsInStore(result.sessionDetail, result.sessions)
    }
  }, [refreshSession, refreshSessionsInStore])

  const handleDeleteCurrentSession = useCallback((): void => {
    if (!currentSessionId) return

    const sessionIdAtShow = currentSessionId

    const handleConfirm = async (): Promise<void> => {
      // Intentionally not awaiting - errors are handled in Actions layer
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

    const modalId = show(
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

    // Type guard: verify modalId is number
    if (typeof modalId === 'number') {
      modalIdReference.current = modalId
    }
  }, [currentSessionId, handleDeleteSession, show, hide])

  return {
    handleDeleteCurrentSession,
    handleDeleteSession,
    handleRefreshSession
  }
}
