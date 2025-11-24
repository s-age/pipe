import { client } from '../client'

export type CreateCompressorRequest = {
  session_id: string
  policy: string
  target_length: number
  start_turn?: number
  end_turn?: number
}

export type CreateCompressorResponse = {
  session_id?: string
  status?: 'approved' | 'rejected' | 'pending'
  summary?: string
  start_turn?: number
  end_turn?: number
  verifier_session_id?: string
  message?: string
}

export const createCompressor = async (
  data: CreateCompressorRequest
): Promise<CreateCompressorResponse> =>
  client.post<CreateCompressorResponse>('/compress', { body: data })

export type ApproveCompressorRequest = {
  session_id: string
}

export type ApproveCompressorResponse = void

export const approveCompressor = async (sessionId: string): Promise<void> =>
  client.post<void>(`/compress/${sessionId}/approve`)

export type DenyCompressorRequest = {
  session_id: string
}

export type DenyCompressorResponse = void

export const denyCompressor = async (sessionId: string): Promise<void> =>
  client.post<void>(`/compress/${sessionId}/deny`)
