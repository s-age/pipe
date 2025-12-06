import { client } from '../client'

export const forkSession = async (
  sessionId: string,
  forkIndex: number
): Promise<{ newSessionId: string }> =>
  client.post<{ newSessionId: string }>(
    `/session/${encodeURIComponent(sessionId)}/fork/${forkIndex}`
  )
