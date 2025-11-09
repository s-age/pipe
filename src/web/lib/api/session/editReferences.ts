import type { Reference } from '@/types/reference'

import { client } from '../client'

export type EditReferencesRequest = {
  references: Reference[]
}

export const editReferences = async (
  sessionId: string,
  references: Reference[],
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/sessions/${sessionId}/references`, {
    body: { references },
  })
