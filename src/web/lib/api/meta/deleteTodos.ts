import { client } from '../client'

export const deleteTodos = async (sessionId: string): Promise<{ message: string }> =>
  client.delete<{ message: string }>(`/session/${sessionId}/todos`)
