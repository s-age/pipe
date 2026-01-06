import type { Hyperparameters } from '@/types/hyperparameters'

import { client } from '../client'

export type EditSessionMetaRequest = {
  artifacts?: string[] | null
  background?: string
  hyperparameters?: Hyperparameters | null
  multiStepReasoningEnabled?: boolean
  procedure?: string | null
  purpose?: string
  roles?: string[] | null
  tokenCount?: number
}

export const editSessionMeta = async (
  sessionId: string,
  meta: EditSessionMetaRequest
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/meta`, {
    body: meta
  })
