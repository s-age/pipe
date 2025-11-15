import type { ChangeEvent } from 'react'
import { useCallback, useState, useRef, useEffect } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import type { Turn } from '@/lib/api/session/getSession'

type UseTurnHandlersProperties = {
  turn: Turn
  index: number
  sessionId: string
  onRefresh: () => Promise<void>
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    newContent: string,
    turn: Turn
  ) => Promise<void>
  showModal: (content: React.ReactNode) => number
  hideModal: (id?: number) => void
  showToastSuccess: (message: string) => void
  showToastFailure: (message: string) => void
}

export const useTurnHandlers = (
  properties: UseTurnHandlersProperties
): {
  isEditing: boolean
  editedContent: string
  handleCopy: () => Promise<void>
  handleEditedChange: (event: ChangeEvent<HTMLTextAreaElement>) => void
  handleCancelEdit: () => void
  handleStartEdit: () => void
  handleFork: () => void
  handleDelete: () => void
  handleSaveEdit: () => void
} => {
  const {
    turn,
    index,
    sessionId,
    onRefresh,
    deleteTurnAction,
    forkSessionAction,
    editTurnAction
  } = properties
  const { show, hide } = useModal()

  const modalIdReference = useRef<number | null>(null)

  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content ?? turn.instruction ?? ''
  )

  // Reset editedContent when turn content changes (after refresh) and not in edit mode
  useEffect(() => {
    if (!isEditing) {
      const newContent = turn.content ?? turn.instruction ?? ''

      setEditedContent(newContent)
    }
  }, [turn.content, turn.instruction, isEditing])

  const handleCopy = useCallback(async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(editedContent)
      emitToast.success('Copied to clipboard')
    } catch {
      emitToast.failure('Failed to copy to clipboard')
    }
  }, [editedContent])

  const handleEditedChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>): void => {
      setEditedContent(event.target.value)
    },
    []
  )

  const handleCancelEdit = useCallback((): void => {
    setIsEditing(false)
    setEditedContent(turn.content ?? turn.instruction ?? '')
  }, [turn.content, turn.instruction])

  const handleStartEdit = useCallback((): void => setIsEditing(true), [])

  const handleConfirmFork = useCallback(async (): Promise<void> => {
    if (modalIdReference.current !== null) {
      await forkSessionAction(sessionId, index)
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [forkSessionAction, sessionId, index, hide])

  const handleCancelFork = useCallback((): void => {
    if (modalIdReference.current !== null) {
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [hide])

  const handleFork = useCallback((): void => {
    modalIdReference.current = show(
      <ConfirmModal
        title="Fork Session"
        message="Do you want to fork a new session from this turn?"
        onConfirm={handleConfirmFork}
        onCancel={handleCancelFork}
        confirmText="Fork"
        cancelText="Cancel"
      />
    )
  }, [show, handleConfirmFork, handleCancelFork])

  const handleConfirmDelete = useCallback(async (): Promise<void> => {
    if (modalIdReference.current !== null) {
      try {
        await deleteTurnAction(sessionId, index)
        await onRefresh()
        emitToast.success('Turn deleted successfully')
      } catch {
        emitToast.failure('Failed to delete turn.')
      } finally {
        hide(modalIdReference.current)
        modalIdReference.current = null
      }
    }
  }, [deleteTurnAction, sessionId, index, onRefresh, hide])

  const handleCancelDelete = useCallback((): void => {
    if (modalIdReference.current !== null) {
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [hide])

  const handleDelete = useCallback((): void => {
    modalIdReference.current = show(
      <ConfirmModal
        title="Delete Turn"
        message="Are you sure you want to delete this turn? This action cannot be undone."
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmText="Delete"
        cancelText="Cancel"
      />
    )
  }, [show, handleConfirmDelete, handleCancelDelete])

  const handleSaveEdit = useCallback(async (): Promise<void> => {
    // Client-side validation
    if (editedContent.trim().length <= 0) {
      emitToast.failure('Content cannot be empty')

      return
    }

    try {
      await editTurnAction(sessionId, index, editedContent, turn)
      await onRefresh()

      setIsEditing(false)
      setEditedContent(turn.content ?? turn.instruction ?? '')
      emitToast.success('Turn updated successfully')
    } catch (error) {
      emitToast.failure(
        `Failed to save changes: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }, [editTurnAction, sessionId, index, editedContent, turn, onRefresh])

  return {
    isEditing,
    editedContent,
    handleCopy,
    handleEditedChange,
    handleCancelEdit,
    handleStartEdit,
    handleFork,
    handleDelete,
    handleSaveEdit
  }
}
