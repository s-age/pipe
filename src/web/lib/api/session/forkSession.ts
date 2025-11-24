import { client } from '../client'

export const forkSession = async (
  sessionId: string,
  forkIndex: number
): Promise<{ new_session_id: string }> =>
  client.post<{ new_session_id: string }>(`/session/${sessionId}/fork/${forkIndex}`)
