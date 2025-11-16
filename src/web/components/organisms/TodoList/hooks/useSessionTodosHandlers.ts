import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { FormMethods } from '@/components/organisms/Form'
import { useSessionTodosActions } from '@/components/organisms/TodoList/hooks/useSessionTodosActions'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

type UseSessionTodosProperties = {
  sessionDetail: SessionDetail | null
}

export const useSessionTodosHandlers = ({
  sessionDetail
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
      if (!sessionDetail?.session_id) return
      void updateTodos(sessionDetail.session_id, todos)
    },
    [sessionDetail, updateTodos]
  )

  const handleDeleteAllTodos = useCallback(async (): Promise<void> => {
    if (!sessionDetail?.session_id) return
    if (!window.confirm('Are you sure you want to delete all todos for this session?'))
      return

    void deleteAllTodos(sessionDetail.session_id)
  }, [sessionDetail, deleteAllTodos])

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
