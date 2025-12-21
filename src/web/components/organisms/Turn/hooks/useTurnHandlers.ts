import type { ChangeEvent } from 'react'
import { useCallback, useRef, useState } from 'react'

import { useModal } from '@/components/organisms/ModalManager'
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
  forkSessionAction: (
    sessionId: string,
    forkIndex: number
  ) => Promise<string | undefined>
}

export const useTurnHandlers = ({
  turn,
  index,
  sessionId,
  onRefresh,
  refreshSessionsInStore,
  deleteTurnAction,
  editTurnAction,
  forkSessionAction
}: UseTurnHandlersProperties): {
  isEditing: boolean
  editedContent: string
  setIsEditing: (isEditing: boolean) => void
  setEditedContent: (editedContent: string) => void
  handleCopy: () => Promise<void>
  handleEditedChange: (event: ChangeEvent<HTMLTextAreaElement>) => void
  handleCancelEdit: () => void
  handleStartEdit: () => void
  handleFork: () => void
  handleDelete: () => void
  handleSaveEdit: () => void
} => {
  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(() => {
    if (turn.type === 'user_task') {
      return turn.instruction
    }
    if (turn.type === 'model_response' || turn.type === 'compressed_history') {
      return turn.content
    }
    if (turn.type === 'function_calling') {
      return turn.response
    }
    if (turn.type === 'tool_response') {
      if (typeof turn.response.message === 'string') {
        return turn.response.message
      }

      return JSON.stringify(turn.response.message, null, 2)
    }

    return ''
  })
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
    let content = ''
    if (turn.type === 'user_task') {
      content = turn.instruction
    } else if (turn.type === 'model_response' || turn.type === 'compressed_history') {
      content = turn.content
    } else if (turn.type === 'function_calling') {
      content = turn.response
    } else if (turn.type === 'tool_response') {
      content =
        typeof turn.response.message === 'string'
          ? turn.response.message
          : JSON.stringify(turn.response.message, null, 2)
    }
    setEditedContent(content)
  }, [turn, setIsEditing, setEditedContent])

  const handleStartEdit = useCallback((): void => setIsEditing(true), [setIsEditing])

  const handleConfirmFork = useCallback(async (): Promise<void> => {
    const currentModalId = modalIdReference.current
    if (currentModalId !== null) {
      try {
        const newSessionId = await forkSessionAction(sessionId, index)
        if (newSessionId) {
          window.location.href = `/session/${newSessionId}`
        }
      } finally {
        hide(currentModalId)
        modalIdReference.current = null
      }
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
    const currentModalId = modalIdReference.current
    if (currentModalId !== null) {
      try {
        await deleteTurnAction(sessionId, index)
        await onRefresh()
        const fetchedSessionDetailResponse = await getSession(sessionId)
        const fetchedSessionTree = await getSessionTree()
        const newSessions = fetchedSessionTree.sessions.map(
          ([id, session]: [string, SessionOverview]) => ({
            ...session,
            sessionId: id
          })
        )
        refreshSessionsInStore(fetchedSessionDetailResponse, newSessions)
      } finally {
        hide(currentModalId)
        modalIdReference.current = null
      }
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
    try {
      await editTurnAction(sessionId, index, editedContent, turn)
      await onRefresh()
      const fetchedSessionDetailResponse = await getSession(sessionId)
      const fetchedSessionTree = await getSessionTree()
      const newSessions = fetchedSessionTree.sessions.map(
        ([id, session]: [string, SessionOverview]) => ({
          ...session,
          sessionId: id
        })
      )
      refreshSessionsInStore(fetchedSessionDetailResponse, newSessions)
    } finally {
      setIsEditing(false)
    }
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
    isEditing,
    editedContent,
    setIsEditing,
    setEditedContent,
    handleCopy,
    handleEditedChange,
    handleCancelEdit,
    handleStartEdit,
    handleFork,
    handleDelete,
    handleSaveEdit
  }
}
