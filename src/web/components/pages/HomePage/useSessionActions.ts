import { useCallback, useState } from 'react'

import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { editTodos, Todo } from '@/lib/api/session/editTodos'
import { forkSession } from '@/lib/api/session/forkSession'
import { SessionData, getSession } from '@/lib/api/session/getSession'

type UseSessionActions = {
  handleDeleteTurn: (sessionId: string, turnIndex: number) => Promise<void>
  handleForkSession: (sessionId: string, forkIndex: number) => Promise<void>
  handleUpdateTodo: (sessionId: string, todos: Todo[]) => Promise<void>
  handleDeleteAllTodos: (sessionId: string) => Promise<void>
  handleUpdateReferencePersist: (
    sessionId: string,
    index: number,
    persist: boolean,
  ) => Promise<void>
  handleUpdateReferenceTtl: (
    sessionId: string,
    index: number,
    ttl: number,
  ) => Promise<void>
  handleUpdateReferenceDisabled: (
    sessionId: string,
    index: number,
    disabled: boolean,
  ) => Promise<void>
  setError: (error: string | null) => void
  setSessionData: (data: SessionData | null) => void
  sessionData: SessionData | null
}

export const useSessionActions = (
  sessionData: SessionData | null,
  setSessionData: (data: SessionData | null) => void,
): UseSessionActions => {
  const setError = useState<string | null>(null)[1]

  const handleDeleteTurn = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      if (!window.confirm('Are you sure you want to delete this turn?')) return
      try {
        await deleteTurn(sessionId, turnIndex)
        const data = await getSession(sessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to delete turn.')
      }
    },
    [setSessionData, setError],
  )

  const handleForkSession = useCallback(
    async (sessionId: string, forkIndex: number): Promise<void> => {
      if (
        !window.confirm(
          `Are you sure you want to fork this session at turn index ${forkIndex + 1}?`,
        )
      )
        return
      try {
        const result = await forkSession(sessionId, forkIndex)
        if (result.new_session_id) {
          window.location.href = `/session/${result.new_session_id}`
        } else {
          throw new Error('Failed to fork session.')
        }
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to fork session.')
      }
    },
    [setError],
  )

  const handleUpdateTodo = useCallback(
    async (sessionId: string, todos: Todo[]): Promise<void> => {
      try {
        await editTodos(sessionId, todos)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update todos.')
      }
    },
    [setError],
  )

  const handleDeleteAllTodos = useCallback(
    async (sessionId: string): Promise<void> => {
      if (
        !window.confirm('Are you sure you want to delete all todos for this session?')
      )
        return
      try {
        await deleteTodos(sessionId)
        const data = await getSession(sessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to delete all todos.')
      }
    },
    [setSessionData, setError],
  )

  const handleUpdateReferencePersist = useCallback(
    async (sessionId: string, index: number, persist: boolean): Promise<void> => {
      try {
        await editReferencePersist(sessionId, index, persist)
        const data = await getSession(sessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference persist state.')
      }
    },
    [setSessionData, setError],
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        const data = await getSession(sessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference TTL.')
      }
    },
    [setSessionData, setError],
  )

  const handleUpdateReferenceDisabled = useCallback(
    async (sessionId: string, index: number, disabled: boolean): Promise<void> => {
      if (!sessionData) return
      try {
        const newReferences = [...sessionData.references]
        newReferences[index] = { ...newReferences[index], disabled }
        await editReferences(sessionId, newReferences)
        const data = await getSession(sessionId)
        setSessionData(data.session)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference disabled state.')
      }
    },
    [sessionData, setSessionData, setError],
  )

  return {
    handleDeleteTurn,
    handleForkSession,
    handleUpdateTodo,
    handleDeleteAllTodos,
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
    setError,
    setSessionData,
    sessionData,
  }
}
