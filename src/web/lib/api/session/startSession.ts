import type { Hyperparameters } from '@/types/hyperparameters'
import type { Reference } from '@/types/reference'

import { client } from '../client'

export type StartSessionRequest = {
  purpose: string
  background: string
  instruction: string
  roles: string[] | null
  parent: string | null
  references: Reference[] | null
  artifacts: string[] | null
  procedure: string | null
  multi_step_reasoning_enabled: boolean
  hyperparameters: Hyperparameters | null
}

export const startSession = async (
  data: StartSessionRequest,
): Promise<{ session_id: string }> =>
  client.post<{ session_id: string }>(`/sessions/start`, {
    body: data,
  })
