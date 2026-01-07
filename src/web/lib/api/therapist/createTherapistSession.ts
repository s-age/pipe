import { client } from '../client'

export type CreateTherapistSessionRequest = {
  sessionId: string
}

export type CreateTherapistSessionResponse = {
  diagnosis: {
    compressions: { end: number; reason: string; start: number }[]
    deletions: number[]
    edits: { newContent: string; turn: number }[]
    summary: string
    rawDiagnosis?: string
  }
  sessionId: string
}

export const createTherapistSession = async (
  data: CreateTherapistSessionRequest
): Promise<CreateTherapistSessionResponse> =>
  client.post<CreateTherapistSessionResponse>('/therapist', {
    body: data
  })
