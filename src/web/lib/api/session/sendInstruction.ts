import { client } from '../client'

export type SendInstructionRequest = {
  instruction: string
}

export const sendInstruction = async (
  sessionId: string,
  instruction: string
): Promise<{ message: string }> =>
  client.post<{ message: string }>(`/session/${sessionId}/instruction`, {
    body: { instruction }
  })
