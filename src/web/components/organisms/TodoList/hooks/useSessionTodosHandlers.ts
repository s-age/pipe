import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import type { FormMethods } from '@/components/organisms/Form'
import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { editTodos } from '@/lib/api/session/editTodos'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

type UseSessionTodosProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  refreshSessions: () => Promise<void>
  // optional setter kept for compatibility; not used here
  setSessionDetail?: (data: SessionDetail | null) => void
}

export const useSessionTodosHandlers = ({
  sessionDetail,
  currentSessionId,
  refreshSessions: _refreshSessions,
  // optional setter kept for compatibility; used to update local detail after actions
  setSessionDetail: _setSessionDetail,
}: UseSessionTodosProperties): {
  handleUpdateTodo: (todos: Todo[]) => Promise<void>
  handleDeleteAllTodos: () => Promise<void>
  handleTodoCheckboxChange: (index?: number) => void
  // optional register for form integration
  register?: FormMethods['register']
  // DOM event helper for checkbox change handlers
  handleCheckboxChange: (event: React.ChangeEvent<HTMLInputElement>) => void
} => {
  const toast = useToast()

  const register = useOptionalFormContext()?.register

  // Perform the API edit; do NOT automatically refresh the parent sessions here.
  // Let the caller (handler) decide whether to call `refreshSessions` to avoid
  // cascading updates that can cause loops.
  const updateTodos = useCallback(
    async (sessionId: string, todos: Todo[]) => {
      try {
        await editTodos(sessionId, todos)
        toast.success('Todos updated')
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to update todos.')
        throw error
      }
    },
    [toast],
  )

  const deleteAllTodos = useCallback(
    async (sessionId: string) => {
      if (
        !window.confirm('Are you sure you want to delete all todos for this session?')
      )
        return

      try {
        await deleteTodos(sessionId)
        toast.success('All todos deleted')
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to delete all todos.')
        throw error
      }
    },
    [toast],
  )

  // NOTE: getSession is available if callers need to fetch a fresh session.

  const handleUpdateTodo = useCallback(
    async (todos: Todo[]) => {
      if (!currentSessionId) return

      await updateTodos(currentSessionId, todos)
      // Update only the session detail to avoid refreshing the entire session tree
      try {
        if (_setSessionDetail) {
          const data = await getSession(currentSessionId)
          _setSessionDetail(data.session)
        }
      } catch {
        // ignore: updateTodos already showed a toast on failure
      }
    },
    [currentSessionId, updateTodos, _setSessionDetail],
  )

  const handleDeleteAllTodos = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return
    await deleteAllTodos(currentSessionId)
    try {
      if (_setSessionDetail) {
        const data = await getSession(currentSessionId)
        _setSessionDetail(data.session)
      }
    } catch {
      // ignore: deleteAllTodos already showed a toast on failure
    }
  }, [currentSessionId, deleteAllTodos, _setSessionDetail])

  const handleTodoCheckboxChange = useCallback(
    (index?: number) => {
      if (index === undefined || !sessionDetail) return

      const newTodos = [...sessionDetail.todos]
      newTodos[Number(index)].checked = !newTodos[Number(index)].checked
      void handleUpdateTodo(newTodos)
    },
    [sessionDetail, handleUpdateTodo],
  )

  const handleCheckboxChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const index = event.currentTarget.dataset.index
      if (!index) return
      handleTodoCheckboxChange(Number(index))
    },
    [handleTodoCheckboxChange],
  )

  return {
    handleUpdateTodo,
    handleDeleteAllTodos,
    handleTodoCheckboxChange,
    register,
    handleCheckboxChange,
  }
}
