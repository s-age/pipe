import { client } from '../client'
import type { SessionDetail } from './getSession'

export type EditMultiStepReasoningRequest = {
  multiStepReasoningEnabled: boolean
}

export const editMultiStepReasoning = async (
  sessionId: string,
  payload: EditMultiStepReasoningRequest
): Promise<{ message: string; session: SessionDetail }> =>
  client.patch<{ message: string; session: SessionDetail }>(
    `/session/${sessionId}/multi_step_reasoning`,
    {
      body: payload
    }
  )
