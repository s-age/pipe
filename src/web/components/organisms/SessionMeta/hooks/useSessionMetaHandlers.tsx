import { useCallback } from 'react'
import type { ChangeEvent } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

type SessionMetaHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  handleDeleteAllTodos: (sessionId: string) => Promise<void>
  handleTodoCheckboxChange: (sessionId: string, todos: Todo[], index: number) => void
  setTemperature: (value: number) => void
  setTopP: (value: number) => void
  setTopK: (value: number) => void
}
export const useSessionMetaHandlers = ({
  currentSessionId,
  sessionDetail,
  handleDeleteAllTodos,
  handleTodoCheckboxChange,
  setTemperature,
  setTopP,
  setTopK,
}: SessionMetaHandlersProperties): {
  handleDeleteAll: () => void
  handleTodoCheckboxChangeWrapper: (event: ChangeEvent<HTMLInputElement>) => void
  handleTemperatureChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleTopPChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleTopKChange: (event: ChangeEvent<HTMLInputElement>) => void
} => {
  const handleDeleteAll = useCallback(() => {
    if (currentSessionId) void handleDeleteAllTodos(currentSessionId)
  }, [currentSessionId, handleDeleteAllTodos])

  const handleTodoCheckboxChangeWrapper = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const index = event.currentTarget.dataset.index
      if (!index || !currentSessionId || !sessionDetail) return
      handleTodoCheckboxChange(currentSessionId, sessionDetail.todos, Number(index))
    },
    [currentSessionId, handleTodoCheckboxChange, sessionDetail],
  )

  const handleTemperatureChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      setTemperature(parseFloat(event.target.value))
    },
    [setTemperature],
  )

  const handleTopPChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      setTopP(parseFloat(event.target.value))
    },
    [setTopP],
  )

  const handleTopKChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      setTopK(parseInt(event.target.value, 10))
    },
    [setTopK],
  )

  return {
    handleDeleteAll,
    handleTodoCheckboxChangeWrapper,
    handleTemperatureChange,
    handleTopPChange,
    handleTopKChange,
  }
}

// Default export removed — use named export `useSessionMetaHandlers`
