import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/meta/deleteTodos'
import { editTodos } from '@/lib/api/meta/editTodos'
import { getSession, type SessionDetail } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'
import type { Todo } from '@/types/todo'

type UseSessionTodosActionsProperties = {
  onSessionDetailUpdate?: (sessionDetail: SessionDetail) => void
}

export const useSessionTodosActions = ({
  onSessionDetailUpdate
}: UseSessionTodosActionsProperties = {}): {
  updateTodos: (sessionId: string, todos: Todo[]) => Promise<void>
  deleteAllTodos: (sessionId: string) => Promise<void>
} => {
  const updateTodos = useCallback(
    async (sessionId: string, todos: Todo[]) => {
      try {
        await editTodos(sessionId, todos)
        addToast({ status: 'success', title: 'Todos updated' })

        // Fetch fresh session detail to ensure UI is in sync
        try {
          const sessionDetail = await getSession(sessionId)
          onSessionDetailUpdate?.(sessionDetail)
        } catch {
          // Silently fail on refresh - the update was still successful
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update todos.'
        })
      }
    },
    [onSessionDetailUpdate]
  )

  const deleteAllTodos = useCallback(
    async (sessionId: string) => {
      try {
        await deleteTodos(sessionId)
        addToast({ status: 'success', title: 'All todos deleted' })

        // Fetch fresh session detail to ensure UI is in sync
        try {
          const sessionDetail = await getSession(sessionId)
          onSessionDetailUpdate?.(sessionDetail)
        } catch {
          // Silently fail on refresh - the delete was still successful
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to delete all todos.'
        })
      }
    },
    [onSessionDetailUpdate]
  )

  return { updateTodos, deleteAllTodos }
}
