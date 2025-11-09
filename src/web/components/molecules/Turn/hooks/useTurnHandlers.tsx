import { useCallback, useState } from 'react'
import type { ChangeEvent } from 'react'

import type { Turn } from '@/lib/api/session/getSession'

type UseTurnHandlersProperties = {
  turn: Turn
  index: number
  sessionId: string
  onDeleteTurn: (sessionId: string, turnIndex: number) => void | Promise<void>
  onForkSession: (sessionId: string, forkIndex: number) => void | Promise<void>
}

export const useTurnHandlers = (
  properties: UseTurnHandlersProperties,
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

  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content ?? turn.instruction ?? '',
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
    [],
  )

  const handleCancelEdit = useCallback((): void => {
    setIsEditing(false)
    setEditedContent(turn.content ?? turn.instruction ?? '')
  }, [turn.content, turn.instruction])

  const handleStartEdit = useCallback((): void => setIsEditing(true), [])

  const handleFork = useCallback((): void => {
    void onForkSession(sessionId, index)
  }, [onForkSession, sessionId, index])

  const handleDelete = useCallback((): void => {
    void onDeleteTurn(sessionId, index)
  }, [onDeleteTurn, sessionId, index])

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
    handleSaveEdit,
  }
}
