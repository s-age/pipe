import { client } from '../client'

export type EditReferencePersistRequest = {
  persist: boolean
}

export const editReferencePersist = async (
  sessionId: string,
  referenceIndex: number,
  persist: boolean,
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(
    `/session/${sessionId}/references/${referenceIndex}/persist`,
    {
      body: { persist },
    },
  )
