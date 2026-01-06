import type { RoleOption } from '@/lib/api/fs/roles'
import type { Reference } from '@/types/reference'
import type { Settings } from '@/types/settings'
import type { Todo } from '@/types/todo'

import { client } from '../client'

export type UserTaskTurn = {
  instruction: string
  timestamp: string
  type: 'user_task'
}

export type ModelResponseTurn = {
  content: string
  timestamp: string
  type: 'model_response'
}

export type FunctionCallingTurn = {
  response: string
  timestamp: string
  type: 'function_calling'
}

export type ToolResponseTurn = {
  name: string
  response: {
    message: string
    status: string
  }
  timestamp: string
  type: 'tool_response'
}

export type CompressedHistoryTurn = {
  content: string
  originalTurnsRange: number[]
  timestamp: string
  type: 'compressed_history'
}

export type Turn =
  | UserTaskTurn
  | ModelResponseTurn
  | FunctionCallingTurn
  | ToolResponseTurn
  | CompressedHistoryTurn

export type SessionDetail = {
  artifacts: string[]
  background: string
  hyperparameters: Settings['hyperparameters'] | null
  instruction: string
  multiStepReasoningEnabled: boolean
  parent: string | null
  procedure: string | null
  purpose: string
  references: Reference[]
  roles: string[]
  sessionId: string | null
  todos: Todo[]
  turns: Turn[]
  roleOptions?: RoleOption[]
  settings?: Settings
  tokenCount?: number
}

export const getSession = async (sessionId: string): Promise<SessionDetail> =>
  client.get<SessionDetail>(`/session/${sessionId}`)
