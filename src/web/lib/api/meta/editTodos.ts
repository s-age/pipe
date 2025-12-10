import type { Todo } from '@/types/todo'

import { client } from '../client'

export type EditTodosRequest = {
  todos: Todo[]
}

export const editTodos = async (
  sessionId: string,
  todos: Todo[]
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/todos`, {
    body: { todos }
  })
