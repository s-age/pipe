import { useCallback } from 'react'

import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { editTodos } from '@/lib/api/session/editTodos'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

export const useTodoActions = (
  setSessionDetail: (data: SessionDetail | null) => void,
  setError: (error: string | null) => void,
  refreshSessions?: () => Promise<void>,
): {
  handleUpdateTodo: (sessionId: string, todos: Todo[]) => Promise<void>
  handleDeleteAllTodos: (sessionId: string) => Promise<void>
  handleTodoCheckboxChange: (sessionId: string, todos: Todo[], index: number) => void
} => {
  const handleUpdateTodo = useCallback(
    async (sessionId: string, todos: Todo[]): Promise<void> => {
      try {
        await editTodos(sessionId, todos)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        setError((error as Error).message || 'Failed to update todos.')
      }
    },
    [setError, refreshSessions],
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
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        setError((error as Error).message || 'Failed to delete all todos.')
      }
    },
    [setSessionDetail, setError, refreshSessions],
  )

  const handleTodoCheckboxChange = useCallback(
    (sessionId: string, todos: Todo[], index: number): void => {
      const newTodos = [...todos]
      newTodos[index].checked = !newTodos[index].checked
      handleUpdateTodo(sessionId, newTodos)
    },
    [handleUpdateTodo],
  )

  return { handleUpdateTodo, handleDeleteAllTodos, handleTodoCheckboxChange }
}
