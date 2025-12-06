import { client } from '../client'

export const editTurn = async (
  sessionId: string,
  turnIndex: number,
  data: Record<string, unknown>
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/turn/${turnIndex}`, {
    body: data
  })
