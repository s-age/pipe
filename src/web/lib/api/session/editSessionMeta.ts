import { Hyperparameters } from '@/types/hyperparameters'

import { client } from '../client'

export type EditSessionMetaRequest = {
  purpose?: string
  background?: string
  roles?: string[] | null
  artifacts?: string[] | null
  procedure?: string | null
  multi_step_reasoning_enabled?: boolean
  token_count?: number
  hyperparameters?: Hyperparameters | null
}

export const editSessionMeta = async (
  sessionId: string,
  meta: EditSessionMetaRequest,
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/meta`, {
    body: meta,
  })
