import { client } from '../client'

export const stopSession = async (sessionId: string): Promise<void> =>
  client.post(`/session/${sessionId}/stop`, {})
