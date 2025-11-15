import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { FormMethods } from '@/components/organisms/Form'
import { useSessionTodosActions } from '@/components/organisms/TodoList/hooks/useSessionTodosActions'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'
import type { Todo } from '@/types/todo'

type UseSessionTodosProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
}

export const useSessionTodosHandlers = ({
  sessionDetail,
  currentSessionId
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

  // NOTE: getSession is available if callers need to fetch a fresh session.

  const handleUpdateTodo = useCallback(
    async (todos: Todo[]) => {
      if (!currentSessionId) return
      try {
        await updateTodos(currentSessionId, todos)
        emitToast.success('Todos updated')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update todos.')
      }
    },
    [currentSessionId, updateTodos]
  )

  const handleDeleteAllTodos = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return
    if (!window.confirm('Are you sure you want to delete all todos for this session?'))
      return

    try {
      await deleteAllTodos(currentSessionId)
      emitToast.success('All todos deleted')
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to delete all todos.')
    }
  }, [currentSessionId, deleteAllTodos])

  const handleTodoCheckboxChange = useCallback(
    (index?: number) => {
      if (typeof index !== 'undefined' && sessionDetail?.todos) {
        const todos = [...sessionDetail.todos]
        const todo = todos[index]
        if (todo) {
          const isChecked = !todo.checked
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
