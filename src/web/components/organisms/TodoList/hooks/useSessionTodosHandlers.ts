import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { FormMethods } from '@/components/organisms/Form'
import { useSessionTodosActions } from '@/components/organisms/TodoList/hooks/useSessionTodosActions'
import { getSession, type SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

type UseSessionTodosProperties = {
  sessionDetail: SessionDetail
  onSessionDetailUpdate?: (sessionDetail: SessionDetail) => void
}

export const useSessionTodosHandlers = ({
  sessionDetail,
  onSessionDetailUpdate
}: UseSessionTodosProperties): {
  handleUpdateTodo: (todos: Todo[]) => Promise<void>
  handleDeleteAllTodos: () => Promise<void>
  handleTodoCheckboxChange: (index?: number) => void
  // optional register for form integration
  register?: FormMethods['register']
  // DOM event helper for checkbox change handlers
  handleCheckboxChange: (event: React.ChangeEvent<HTMLInputElement>) => void
} => {
  const register = useOptionalFormContext()?.register

  const { updateTodos, deleteAllTodos } = useSessionTodosActions()

  const handleUpdateTodo = useCallback(
    async (todos: Todo[]) => {
      if (!sessionDetail.sessionId) return
      await updateTodos(sessionDetail.sessionId, todos)

      // Fetch fresh session detail to ensure UI is in sync
      try {
        const freshSessionDetail = await getSession(sessionDetail.sessionId)
        onSessionDetailUpdate?.(freshSessionDetail)
      } catch {
        // Silently fail on refresh - the update was still successful
      }
    },
    [sessionDetail, updateTodos, onSessionDetailUpdate]
  )

  const handleDeleteAllTodos = useCallback(async (): Promise<void> => {
    if (!sessionDetail.sessionId) return
    if (!window.confirm('Are you sure you want to delete all todos for this session?'))
      return

    await deleteAllTodos(sessionDetail.sessionId)

    // Fetch fresh session detail to ensure UI is in sync
    try {
      const freshSessionDetail = await getSession(sessionDetail.sessionId)
      onSessionDetailUpdate?.(freshSessionDetail)
    } catch {
      // Silently fail on refresh - the delete was still successful
    }
  }, [sessionDetail, deleteAllTodos, onSessionDetailUpdate])

  const handleTodoCheckboxChange = useCallback(
    (index?: number) => {
      if (typeof index !== 'undefined' && sessionDetail.todos) {
        const todos = [...sessionDetail.todos]
        const todo = todos[index]
        if (todo) {
          const isChecked = !todo.checked
          // Intentionally not awaiting - errors are handled in Actions layer
          void handleUpdateTodo(
            todos.map((t, i) => (i === index ? { ...t, checked: isChecked } : t))
          )
        }
      }
    },
    [handleUpdateTodo, sessionDetail]
  )

  const handleCheckboxChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const index = Number(event.target.dataset.index)
      if (isNaN(index)) return
      handleTodoCheckboxChange(index)
    },
    [handleTodoCheckboxChange]
  )

  return {
    register,
    handleUpdateTodo,
    handleDeleteAllTodos,
    handleTodoCheckboxChange,
    handleCheckboxChange
  }
}
