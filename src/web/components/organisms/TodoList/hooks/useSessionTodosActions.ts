import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/meta/deleteTodos'
import { editTodos } from '@/lib/api/meta/editTodos'
import { addToast } from '@/stores/useToastStore'
import type { Todo } from '@/types/todo'

export const useSessionTodosActions = (): {
  deleteAllTodos: (sessionId: string) => Promise<void>
  updateTodos: (sessionId: string, todos: Todo[]) => Promise<void>
} => {
  const updateTodos = useCallback(async (sessionId: string, todos: Todo[]) => {
    try {
      await editTodos(sessionId, todos)
      addToast({ status: 'success', title: 'Todos updated' })
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to update todos.'
      })
    }
  }, [])

  const deleteAllTodos = useCallback(async (sessionId: string) => {
    try {
      await deleteTodos(sessionId)
      addToast({ status: 'success', title: 'All todos deleted' })
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to delete all todos.'
      })
    }
  }, [])

  return { updateTodos, deleteAllTodos }
}
