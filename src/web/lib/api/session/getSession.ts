import type { Hyperparameters } from '@/types/hyperparameters'
import type { Reference } from '@/types/reference'
import type { Todo } from '@/types/todo'

import { client } from '../client'

export type Turn = {
  type:
    | 'user_task'
    | 'model_response'
    | 'function_calling'
    | 'tool_response'
    | 'compressed_history'
    | 'unknown'
  instruction?: string
  content?: string
  response?: {
    status?: 'success' | 'error'
    output?: unknown
    [key: string]: unknown
  }
  timestamp?: string
  [key: string]: unknown
}

export type SessionDetail = {
  id: string | undefined
  purpose: string
  background: string
  roles: string[]
  procedure: string
  artifacts: string[]
  multi_step_reasoning_enabled: boolean
  hyperparameters: Hyperparameters
  todos: Todo[]
  references: Reference[]
  turns: Turn[]
}

export const getSession = async (
  sessionId: string,
): Promise<{ session: SessionDetail }> =>
  client.get<{ session: SessionDetail }>(`/session/${sessionId}`)
