import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { FormMethods } from '@/components/organisms/Form'
import { useSessionTodosActions } from '@/components/organisms/TodoList/hooks/useSessionTodosActions'
import type { SessionDetail } from '@/lib/api/session/getSession'
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
      await updateTodos(currentSessionId, todos)
    },
    [currentSessionId, updateTodos]
  )

  const handleDeleteAllTodos = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return
    await deleteAllTodos(currentSessionId)
  }, [currentSessionId, deleteAllTodos])

  const handleTodoCheckboxChange = useCallback(
    (index?: number) => {
      if (typeof index !== 'undefined' && sessionDetail?.todos) {
        const todos = [...sessionDetail.todos]
        const todo = todos[index]
        if (todo) {
          const isChecked = !todo.checked
          handleUpdateTodo(
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
