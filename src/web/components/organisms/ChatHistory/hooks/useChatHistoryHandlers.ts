import React, { useCallback, useRef } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { useModal } from '@/components/molecules/Modal/hooks/useModal'
import { emitToast } from '@/lib/toastEvents'

import { useChatHistoryActions } from './useChatHistoryActions'

type UseChatHistoryHandlersProperties = {
  currentSessionId: string | null
}

export const useChatHistoryHandlers = ({
  currentSessionId
}: UseChatHistoryHandlersProperties): {
  handleDeleteCurrentSession: () => void
  handleDeleteSession: (sessionId: string) => Promise<void>
} => {
  const { show, hide } = useModal()
  const { deleteSessionAction } = useChatHistoryActions({ currentSessionId })

  const modalIdReference = useRef<number | null>(null)

  const handleDeleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      try {
        await deleteSessionAction(sessionId)
        emitToast.success('Session deleted')
        location.href = '/'
      } catch {
        emitToast.failure('Failed to delete session.')
      }
    },
    [deleteSessionAction]
  )

  const handleDeleteCurrentSession = useCallback((): void => {
    if (!currentSessionId) return

    const sessionIdAtShow = currentSessionId

    const handleConfirm = (): void => {
      try {
        void handleDeleteSession(sessionIdAtShow)
      } catch (error) {
        console.error('Error deleting session:', error)
      }
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
    ) as unknown as number
  }, [currentSessionId, handleDeleteSession, hide, show])

  return {
    handleDeleteCurrentSession,
    handleDeleteSession
  }
}

export type { UseChatHistoryHandlersProperties }
