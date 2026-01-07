import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Strong } from '@/components/atoms/Strong'
import { Box } from '@/components/molecules/Box'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputCheckbox } from '@/components/molecules/InputCheckbox'
import { ListItem } from '@/components/molecules/ListItem'
import { MetaItem } from '@/components/molecules/MetaItem'
import { Paragraph } from '@/components/molecules/Paragraph'
import { UnorderedList } from '@/components/molecules/UnorderedList'
import { useSessionTodosHandlers } from '@/components/organisms/TodoList/hooks/useSessionTodosHandlers'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Todo } from '@/types/todo'

import {
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
          <Box>
            {sessionDetail && sessionDetail.todos.length > 0 ? (
              <UnorderedList>
                {sessionDetail.todos.map((todo: Todo, index: number) => (
                  <ListItem key={index} className={todoItem}>
                    <Box className={todoCheckboxLabel}>
                      <Box className={todoCheckboxMargin}>
                        <InputCheckbox
                          register={register}
                          name={`todos[${index}].checked`}
                          defaultChecked={todo.checked}
                          onChange={handleCheckboxChange}
                          data-index={String(index)}
                        />
                      </Box>
                      <Strong className={todoTitle}>{todo.title}</Strong>
                    </Box>
                  </ListItem>
                ))}
              </UnorderedList>
            ) : (
              <Paragraph className={noItemsMessage}>
                No todos for this session.
              </Paragraph>
            )}

            <Button
              className={deleteTodosButton}
              kind="secondary"
              size="default"
              onClick={handleDeleteAllTodos}
            >
              Delete All Todos
            </Button>
          </Box>
        )}
      </Fieldset>
    </MetaItem>
  )
}
