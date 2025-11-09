import { client } from '../client'
import type { SessionDetail } from './getSession'

export type EditMultiStepReasoningRequest = {
  multi_step_reasoning_enabled: boolean
}

export const editMultiStepReasoning = async (
  sessionId: string,
  payload: EditMultiStepReasoningRequest,
): Promise<{ message: string; session: SessionDetail }> =>
  client.patch<{ message: string; session: SessionDetail }>(
    `/session/${sessionId}/multi-step-reasoning`,
    {
      body: payload,
    },
  )
