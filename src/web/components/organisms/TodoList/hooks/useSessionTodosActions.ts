import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { editTodos } from '@/lib/api/session/editTodos'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'
import type { Todo } from '@/types/todo'

export const useSessionTodosActions = (): {
  updateTodos: (
    sessionId: string,
    todos: Todo[],
    refreshSessions?: () => Promise<void>
  ) => Promise<void>
  deleteAllTodos: (
    sessionId: string,
    refreshSessions?: () => Promise<void>
  ) => Promise<void>
  fetchSession: (sessionId: string) => Promise<SessionDetail>
} => {
  const updateTodos = useCallback(
    async (sessionId: string, todos: Todo[], refreshSessions?: () => Promise<void>) => {
      try {
        await editTodos(sessionId, todos)
        if (refreshSessions) await refreshSessions()
        emitToast.success('Todos updated')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update todos.')
        throw error
      }
    },
    []
  )

  const deleteAllTodos = useCallback(
    async (sessionId: string, refreshSessions?: () => Promise<void>) => {
      if (
        !window.confirm('Are you sure you want to delete all todos for this session?')
      )
        return

      try {
        await deleteTodos(sessionId)
        // prefer refreshSessions to allow a single canonical refresh
        if (refreshSessions) await refreshSessions()
        emitToast.success('All todos deleted')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to delete all todos.')
        throw error
      }
    },
    []
  )

  const fetchSession = useCallback(async (sessionId: string) => {
    const data = await getSession(sessionId)

    return data.session
  }, [])

  return { updateTodos, deleteAllTodos, fetchSession }
}
