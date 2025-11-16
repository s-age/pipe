import type { SessionDetail } from './getSession'
import { client } from '../client'

export type EditHyperparametersRequest = Partial<{
  temperature: number
  top_p: number
  top_k: number
}>

export const editHyperparameters = async (
  sessionId: string,
  hyperparameters: EditHyperparametersRequest
): Promise<{ message: string; session: SessionDetail }> =>
  client.patch<{ message: string; session: SessionDetail }>(
    `/session/${sessionId}/hyperparameters`,
    {
      body: hyperparameters
    }
  )
