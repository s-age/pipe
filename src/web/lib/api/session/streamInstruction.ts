import { streamingClient } from '../streamingClient'

export type StreamInstructionOptions = {
  instruction: string
  signal?: AbortSignal
}

/**
 * Stream instruction to a session.
 * Returns a ReadableStream for processing streaming text responses.
 *
 * @param sessionId - The ID of the session
 * @param options - Instruction text and optional AbortSignal
 * @returns ReadableStream<Uint8Array> for processing chunks
 */
export const streamInstruction = async (
  sessionId: string,
  options: StreamInstructionOptions
): Promise<ReadableStream<Uint8Array>> =>
  streamingClient.post(`/session/${sessionId}/instruction`, {
    body: { instruction: options.instruction },
    signal: options.signal
  })
