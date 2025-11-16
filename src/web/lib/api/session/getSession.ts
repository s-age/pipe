import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { Reference } from '@/types/reference'
import type { Settings } from '@/types/settings'
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
  session_id: string | null
  purpose: string
  background: string
  roles: string[]
  parent: string | null
  references: Reference[]
  artifacts: string[]
  procedure: string | null
  instruction: string
  multi_step_reasoning_enabled: boolean
  hyperparameters: Settings['hyperparameters'] | null
  todos: Todo[]
  turns: Turn[]
  roleOptions?: RoleOption[]
}

export const getSession = async (
  sessionId: string
): Promise<{ session: SessionDetail }> =>
  client.get<{ session: SessionDetail }>(`/session/${sessionId}`)
