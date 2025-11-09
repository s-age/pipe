import { client } from '../client'

export type ForkSessionRequest = {
  fork_index: number
}

export const forkSession = async (
  sessionId: string,
  forkIndex: number
): Promise<{ new_session_id: string }> =>
  client.post<{ new_session_id: string }>(`/sessions/${sessionId}/fork`, {
    body: { fork_index: forkIndex }
  })
