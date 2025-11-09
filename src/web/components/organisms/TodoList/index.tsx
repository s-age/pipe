import React from 'react'

import { Button } from '@/components/atoms/Button'
import { InputCheckbox } from '@/components/atoms/InputCheckbox'
import { Fieldset } from '@/components/molecules/Fieldset'
import { useSessionTodosHandlers } from '@/components/organisms/TodoList/hooks/useSessionTodosHandlers'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

import {
  metaItem,
  todosList,
  todoItem,
  todoCheckboxLabel,
  todoTitle,
  noItemsMessage,
  deleteTodosButton,
  todoCheckboxMargin
} from './style.css'

type TodoListProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
}

export const TodoList = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail: _setSessionDetail,
  refreshSessions
}: TodoListProperties): React.JSX.Element => {
  const { register, handleDeleteAllTodos, handleCheckboxChange } =
    useSessionTodosHandlers({
      sessionDetail,
      currentSessionId,
      refreshSessions
    })

  return (
    <div className={metaItem}>
      <Fieldset legend="Todos">
        {() => (
          <div>
            <Button
              className={deleteTodosButton}
              kind="secondary"
              size="default"
              onClick={handleDeleteAllTodos}
            >
              Delete All
            </Button>

            {sessionDetail && sessionDetail.todos.length > 0 ? (
              <ul className={todosList}>
                {sessionDetail.todos.map((todo: Todo, index: number) => (
                  <li key={index} className={todoItem}>
                    <div className={todoCheckboxLabel}>
                      <div className={todoCheckboxMargin}>
                        <InputCheckbox
                          register={register}
                          name={`todos[${index}].checked`}
                          defaultChecked={todo.checked}
                          onChange={handleCheckboxChange}
                          data-index={String(index)}
                        />
                      </div>
                      <strong className={todoTitle}>{todo.title}</strong>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={noItemsMessage}>No todos for this session.</p>
            )}
          </div>
        )}
      </Fieldset>
    </div>
  )
}
