import { useCallback, useState, useRef } from 'react'
import type { ChangeEvent } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { useModal } from '@/components/molecules/Modal/hooks/useModal'
import { useTurnActions } from '@/components/organisms/ChatHistory/hooks/useTurnActions'
import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { Turn } from '@/lib/api/session/getSession'

type UseTurnHandlersProperties = {
  turn: Turn
  index: number
  sessionId: string
  onRefresh: () => Promise<void>
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
  const { turn, index, sessionId, onRefresh } = properties
  const { show, hide } = useModal()
  const { deleteTurnAction, forkSessionAction, editTurnAction } =
    useTurnActions(onRefresh)

  const modalIdReference = useRef<number | null>(null)

  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content ?? turn.instruction ?? ''
  )

  const toast = useToast()

  const handleCopy = useCallback(async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(editedContent)
      toast.success('Copied to clipboard')
    } catch {
      toast.failure('Failed to copy to clipboard')
    }
  }, [editedContent, toast])

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
      await deleteTurnAction(sessionId, index)
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [deleteTurnAction, sessionId, index, hide])

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
    console.log(`Saving turn ${index} with new content: ${editedContent}`)
    await editTurnAction(sessionId, index, editedContent)
    setIsEditing(false)
  }, [index, editedContent, sessionId, editTurnAction])

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
