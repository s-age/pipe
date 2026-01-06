import { client } from '../client'
import type { SessionDetail } from '../session/getSession'

export type EditHyperparametersRequest = Partial<{
  temperature: number
  topK: number
  topP: number
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
