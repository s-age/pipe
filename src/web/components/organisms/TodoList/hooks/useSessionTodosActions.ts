import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { editTodos } from '@/lib/api/session/editTodos'
import { emitToast } from '@/lib/toastEvents'
import type { Todo } from '@/types/todo'

export const useSessionTodosActions = (): {
  updateTodos: (sessionId: string, todos: Todo[]) => Promise<void>
  deleteAllTodos: (sessionId: string) => Promise<void>
} => {
  const updateTodos = useCallback(async (sessionId: string, todos: Todo[]) => {
    try {
      await editTodos(sessionId, todos)
      emitToast.success('Todos updated')
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to update todos.')
    }
  }, [])

  const deleteAllTodos = useCallback(async (sessionId: string) => {
    try {
      await deleteTodos(sessionId)
      emitToast.success('All todos deleted')
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to delete all todos.')
    }
  }, [])

  return { updateTodos, deleteAllTodos }
}
