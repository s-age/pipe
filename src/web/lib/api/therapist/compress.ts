import { client } from '../client'

export type CreateCompressorRequest = {
  sessionId: string
  policy: string
  targetLength: number
  startTurn?: number
  endTurn?: number
}

export type CreateCompressorResponse = {
  sessionId?: string
  status?: 'approved' | 'rejected' | 'pending'
  summary?: string
  startTurn?: number
  endTurn?: number
  verifierSessionId?: string
  message?: string
}

export const createCompressor = async (
  data: CreateCompressorRequest
): Promise<CreateCompressorResponse> =>
  client.post<CreateCompressorResponse>('/compress', { body: data })

export type ApproveCompressorRequest = {
  sessionId: string
}

export type ApproveCompressorResponse = void

export const approveCompressor = async (sessionId: string): Promise<void> =>
  client.post<void>(`/compress/${sessionId}/approve`)

export type DenyCompressorRequest = {
  sessionId: string
}

export type DenyCompressorResponse = void

export const denyCompressor = async (sessionId: string): Promise<void> =>
  client.post<void>(`/compress/${sessionId}/deny`)
