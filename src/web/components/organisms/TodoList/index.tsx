import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
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
  sessionDetail: SessionDetail
}

export const TodoList = ({ sessionDetail }: TodoListProperties): React.JSX.Element => {
  const { register, handleDeleteAllTodos, handleCheckboxChange } =
    useSessionTodosHandlers({
      sessionDetail
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
