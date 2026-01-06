import type { Hyperparameters } from '@/types/hyperparameters'
import type { Reference } from '@/types/reference'

import { client } from '../client'

export type StartSessionRequest = {
  artifacts: string[] | null
  background: string
  hyperparameters: Hyperparameters | null
  instruction: string
  multiStepReasoningEnabled: boolean
  parent: string | null
  procedure: string | null
  purpose: string
  references: Reference[] | null
  roles: string[] | null
}

export const startSession = async (
  data: StartSessionRequest
): Promise<{ sessionId: string }> =>
  client.post<{ sessionId: string }>('/session/start', {
    body: data
  })
