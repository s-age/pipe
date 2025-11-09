import { client } from '../client'

export type SendInstructionRequest = {
  instruction: string
}

export const sendInstruction = async (
  sessionId: string,
  instruction: string
): Promise<unknown> =>
  client.post<unknown>(`/session/${sessionId}/instruction`, {
    body: { instruction }
  })
