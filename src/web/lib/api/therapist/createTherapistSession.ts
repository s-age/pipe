import { client } from '../client'

export type CreateTherapistSessionRequest = {
  sessionId: string
}

export type CreateTherapistSessionResponse = {
  sessionId: string
  diagnosis: {
    deletions: number[]
    edits: { turn: number; newContent: string }[]
    compressions: { start: number; end: number; reason: string }[]
    summary: string
    rawDiagnosis?: string
  }
}

export const createTherapistSession = async (
  data: CreateTherapistSessionRequest
): Promise<CreateTherapistSessionResponse> =>
  client.post<CreateTherapistSessionResponse>('/therapist', {
    body: data
  })
