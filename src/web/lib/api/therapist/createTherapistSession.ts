import { client } from '../client'

export type CreateTherapistSessionRequest = {
  session_id: string
}

export type CreateTherapistSessionResponse = {
  session_id: string
  diagnosis: {
    deletions: number[]
    edits: { turn: number; suggestion: string }[]
    compressions: { start: number; end: number; reason: string }[]
    summary: string
    raw_diagnosis?: string
  }
}

export const createTherapistSession = async (
  data: CreateTherapistSessionRequest
): Promise<CreateTherapistSessionResponse> =>
  client.post<CreateTherapistSessionResponse>('/therapist', {
    body: data
  })
