import { client } from '../client'

export type CreateCompressorRequest = {
  endTurn: number
  policy: string
  sessionId: string
  startTurn: number
  targetLength: number
}

export type CreateCompressorResponse = {
  message?: string
  sessionId?: string
  summary?: string
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
