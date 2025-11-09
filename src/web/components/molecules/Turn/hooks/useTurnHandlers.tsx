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

export function useTurnHandlers({
  turn,
  index,
  sessionId,
  onDeleteTurn,
  onForkSession,
}: UseTurnHandlersProperties): {
  isEditing: boolean
  editedContent: string
  handleCopy: () => Promise<void>
  handleEditedChange: (event: ChangeEvent<HTMLTextAreaElement>) => void
  handleCancelEdit: () => void
  handleStartEdit: () => void
  handleFork: () => void
  handleDelete: () => void
  handleSaveEdit: () => void
} {
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content || turn.instruction || '',
  )

  const handleCopy = useCallback(async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(editedContent)
      alert('Copied!')
    } catch (error) {
      console.error('Failed to copy: ', error)
      alert('Failed to copy')
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
  }, [])

  const handleStartEdit = useCallback((): void => {
    setIsEditing(true)
  }, [])

  const handleFork = useCallback((): void => {
    onForkSession(sessionId, index)
  }, [onForkSession, sessionId, index])

  const handleDelete = useCallback((): void => {
    onDeleteTurn(sessionId, index)
  }, [onDeleteTurn, sessionId, index])

  const handleSaveEdit = useCallback((): void => {
    // TODO: API呼び出しを実装する
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
