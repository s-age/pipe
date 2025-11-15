import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { editTodos } from '@/lib/api/session/editTodos'
import type { Todo } from '@/types/todo'

export const useSessionTodosActions = (): {
  updateTodos: (sessionId: string, todos: Todo[]) => Promise<void>
  deleteAllTodos: (sessionId: string) => Promise<void>
} => {
  const updateTodos = useCallback(async (sessionId: string, todos: Todo[]) => {
    await editTodos(sessionId, todos)
  }, [])

  const deleteAllTodos = useCallback(async (sessionId: string) => {
    await deleteTodos(sessionId)
  }, [])

  return { updateTodos, deleteAllTodos }
}
