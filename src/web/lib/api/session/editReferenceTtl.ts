import { client } from '../client'

export type EditReferenceTtlRequest = {
  ttl: number
}

export const editReferenceTtl = async (
  sessionId: string,
  referenceIndex: number,
  ttl: number
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(
    `/sessions/${sessionId}/references/${referenceIndex}/ttl`,
    {
      body: { ttl }
    }
  )
