import { client } from '../client'
import { Turn } from './getSession'

export const getTurns = async (
  sessionId: string,
  since: number = 0,
): Promise<{ turns: Turn[] }> =>
  client.get<{ turns: Turn[] }>(`/session/${sessionId}/turns?since=${since}`)
