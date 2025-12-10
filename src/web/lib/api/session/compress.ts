import { client } from '../client'

export type CreateCompressorRequest = {
  sessionId: string
  policy: string
  targetLength: number
  startTurn: number
  endTurn: number
}

export type CreateCompressorResponse = {
  sessionId?: string
  summary?: string
  message?: string
}

export const createCompressor = async (
  request: CreateCompressorRequest
): Promise<CreateCompressorResponse> =>
  client.post<CreateCompressorResponse>('/session/compress', {
    body: request
  })

export const approveCompressor = async (
  compressorSessionId: string
): Promise<{ message: string }> =>
  client.post<{ message: string }>(`/session/compress/${compressorSessionId}/approve`)

export const denyCompressor = async (
  compressorSessionId: string
): Promise<{ message: string }> =>
  client.post<{ message: string }>(`/session/compress/${compressorSessionId}/deny`)
