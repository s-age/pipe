import { client } from '../client'

export type CreateCompressorRequest = {
  policy: string
  sessionId: string
  targetLength: number
  endTurn?: number
  startTurn?: number
}

export type CreateCompressorResponse = {
  endTurn?: number
  message?: string
  sessionId?: string
  startTurn?: number
  status?: 'approved' | 'rejected' | 'pending'
  summary?: string
  verifierSessionId?: string
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
