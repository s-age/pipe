import type { ChangeEvent } from 'react'
import { useCallback, useRef } from 'react'

import { useModal } from '@/components/molecules/Modal/hooks/useModal'
import { getSession } from '@/lib/api/session/getSession'
import type { Turn } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useToast } from '../../Toast/hooks/useToast'

type UseTurnHandlersProperties = {
  turn: Turn
  index: number
  sessionId: string
  editedContent: string
  setIsEditing: (isEditing: boolean) => void
  setEditedContent: (editedContent: string) => void
  onRefresh: () => Promise<void>
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
  deleteTurnAction: (sessionId: string, turnIndex: number) => Promise<void>
  editTurnAction: (
    sessionId: string,
    turnIndex: number,
    new_content: string,
    turn: Turn
  ) => Promise<void>
  forkSessionAction: (sessionId: string, forkIndex: number) => Promise<void>
}

export const useTurnHandlers = ({
  turn,
  index,
  sessionId,
  editedContent,
  setIsEditing,
  setEditedContent,
  onRefresh,
  refreshSessionsInStore,
  deleteTurnAction,
  editTurnAction,
  forkSessionAction
}: UseTurnHandlersProperties): {
  handleCopy: () => Promise<void>
  handleEditedChange: (event: ChangeEvent<HTMLTextAreaElement>) => void
  handleCancelEdit: () => void
  handleStartEdit: () => void
  handleFork: () => void
  handleDelete: () => void
  handleSaveEdit: () => void
} => {
  const { show, hide } = useModal()

  const modalIdReference = useRef<number | null>(null)
  const toast = useToast()

  const handleCopy = useCallback(async (): Promise<void> => {
    await navigator.clipboard.writeText(editedContent)

    toast.addToast({ status: 'success', title: 'Copied to clipboard.' })
  }, [editedContent, toast])

  const handleEditedChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>): void => {
      setEditedContent(event.target.value)
    },
    [setEditedContent]
  )

  const handleCancelEdit = useCallback((): void => {
    setIsEditing(false)
    setEditedContent(turn.content ?? turn.instruction ?? '')
  }, [turn.content, turn.instruction, setIsEditing, setEditedContent])

  const handleStartEdit = useCallback((): void => setIsEditing(true), [setIsEditing])

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
    modalIdReference.current = show({
      type: 'confirm',
      props: {
        title: 'Fork Session',
        message: 'Are you sure you want to fork this session?',
        onConfirm: handleConfirmFork,
        onCancel: handleCancelFork
      }
    })
  }, [show, handleConfirmFork, handleCancelFork])

  const handleConfirmDelete = useCallback(async (): Promise<void> => {
    if (modalIdReference.current !== null) {
      await deleteTurnAction(sessionId, index)
      await onRefresh()
      const fetchedSessionDetailResponse = await getSession(sessionId)
      const fetchedSessionTree = await getSessionTree()
      const newSessions = fetchedSessionTree.sessions.map(([id, session]) => ({
        ...session,
        sessionId: id
      }))
      refreshSessionsInStore(fetchedSessionDetailResponse.session, newSessions)
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [deleteTurnAction, sessionId, index, onRefresh, refreshSessionsInStore, hide])

  const handleCancelDelete = useCallback((): void => {
    if (modalIdReference.current !== null) {
      hide(modalIdReference.current)
      modalIdReference.current = null
    }
  }, [hide])

  const handleDelete = useCallback((): void => {
    modalIdReference.current = show({
      type: 'confirm',
      props: {
        title: 'Delete Turn',
        message: 'Are you sure you want to delete this turn?',
        onConfirm: handleConfirmDelete,
        onCancel: handleCancelDelete
      }
    })
  }, [show, handleConfirmDelete, handleCancelDelete])

  const handleSaveEdit = useCallback(async (): Promise<void> => {
    await editTurnAction(sessionId, index, editedContent, turn)
    await onRefresh()
    const fetchedSessionDetailResponse = await getSession(sessionId)
    const fetchedSessionTree = await getSessionTree()
    const newSessions = fetchedSessionTree.sessions.map(([id, session]) => ({
      ...session,
      sessionId: id
    }))
    refreshSessionsInStore(fetchedSessionDetailResponse.session, newSessions)
    setIsEditing(false)
  }, [
    editTurnAction,
    sessionId,
    index,
    editedContent,
    turn,
    onRefresh,
    refreshSessionsInStore,
    setIsEditing
  ])

  return {
    handleCopy,
    handleEditedChange,
    handleCancelEdit,
    handleStartEdit,
    handleFork,
    handleDelete,
    handleSaveEdit
  }
}
