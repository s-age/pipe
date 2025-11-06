import { client } from '../client'

export const deleteTurn = async (
  sessionId: string,
  turnIndex: number,
): Promise<{ message: string }> =>
  client.delete<{ message: string }>(`/session/${sessionId}/turn/${turnIndex}`)
