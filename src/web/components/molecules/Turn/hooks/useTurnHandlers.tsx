import { useCallback, useState, useRef } from 'react'
import type { ChangeEvent } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { useModal } from '@/components/molecules/Modal/hooks/useModal'
import type { Turn } from '@/lib/api/session/getSession'

type UseTurnHandlersProperties = {
  turn: Turn
  index: number
  sessionId: string
  onDeleteTurn: (sessionId: string, turnIndex: number) => void | Promise<void>
  onForkSession: (sessionId: string, forkIndex: number) => void | Promise<void>
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
  const { turn, index, sessionId, onDeleteTurn, onForkSession } = properties
  const { show, hide } = useModal()

  const modalIdReference = useRef<number | null>(null)

  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content ?? turn.instruction ?? ''
  )

  const handleCopy = useCallback(async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(editedContent)
    } catch (error) {
      console.error('Failed to copy: ', error)
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

  const handleConfirmFork = useCallback((): void => {
    if (modalIdReference.current !== null) {
      void onForkSession(sessionId, index)
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [onForkSession, sessionId, index, hide])

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

  const handleConfirmDelete = useCallback((): void => {
    if (modalIdReference.current !== null) {
      void onDeleteTurn(sessionId, index)
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [onDeleteTurn, sessionId, index, hide])

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

  const handleSaveEdit = useCallback((): void => {
    console.log(`Saving turn ${index} with new content: ${editedContent}`)
    setIsEditing(false)
  }, [index, editedContent])

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
