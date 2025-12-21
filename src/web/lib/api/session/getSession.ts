import type { RoleOption } from '@/lib/api/fs/roles'
import type { Reference } from '@/types/reference'
import type { Settings } from '@/types/settings'
import type { Todo } from '@/types/todo'

import { client } from '../client'

export type UserTaskTurn = {
  type: 'user_task'
  instruction: string
  timestamp: string
}

export type ModelResponseTurn = {
  type: 'model_response'
  content: string
  timestamp: string
}

export type FunctionCallingTurn = {
  type: 'function_calling'
  response: string
  timestamp: string
}

export type ToolResponseTurn = {
  type: 'tool_response'
  name: string
  response: {
    status: string
    message: string
  }
  timestamp: string
}

export type CompressedHistoryTurn = {
  type: 'compressed_history'
  content: string
  originalTurnsRange: number[]
  timestamp: string
}

export type Turn =
  | UserTaskTurn
  | ModelResponseTurn
  | FunctionCallingTurn
  | ToolResponseTurn
  | CompressedHistoryTurn

export type SessionDetail = {
  sessionId: string | null
  purpose: string
  background: string
  roles: string[]
  parent: string | null
  references: Reference[]
  artifacts: string[]
  procedure: string | null
  instruction: string
  multiStepReasoningEnabled: boolean
  hyperparameters: Settings['hyperparameters'] | null
  // tokenCount and settings are returned by the server in some endpoints
  // (e.g. session dashboard). Make them optional so callers can use them
  // when available without causing type errors.
  tokenCount?: number
  settings?: Settings
  todos: Todo[]
  turns: Turn[]
  roleOptions?: RoleOption[]
}

export const getSession = async (sessionId: string): Promise<SessionDetail> =>
  client.get<SessionDetail>(`/session/${sessionId}`)
