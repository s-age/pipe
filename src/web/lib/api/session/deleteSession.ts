import { client } from '../client'

export const deleteSession = async (sessionId: string): Promise<void> => {
  await client.delete<void>(`/session/${sessionId}`)
}
