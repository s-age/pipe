import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { MetaItem } from '@/components/molecules/MetaItem'
import { useSessionTodosHandlers } from '@/components/organisms/TodoList/hooks/useSessionTodosHandlers'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

import {
  todosList,
  todoItem,
  todoCheckboxLabel,
  todoTitle,
  noItemsMessage,
  deleteTodosButton,
  todoCheckboxMargin
} from './style.css'

type TodoListProperties = {
  sessionDetail: SessionDetail
  onSessionDetailUpdate?: (sessionDetail: SessionDetail) => void
}

export const TodoList = ({
  sessionDetail,
  onSessionDetailUpdate
}: TodoListProperties): React.JSX.Element => {
  const { handleCheckboxChange, handleDeleteAllTodos, register } =
    useSessionTodosHandlers({
      sessionDetail,
      onSessionDetailUpdate
    })

  return (
    <MetaItem>
      <Fieldset legend="Todos">
        {() => (
          <div>
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

            <Button
              className={deleteTodosButton}
              kind="secondary"
              size="default"
              onClick={handleDeleteAllTodos}
            >
              Delete All Todos
            </Button>
          </div>
        )}
      </Fieldset>
    </MetaItem>
  )
}
