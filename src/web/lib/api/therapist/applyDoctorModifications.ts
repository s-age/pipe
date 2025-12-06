import { client } from '../client'

export type ApplyDoctorModificationsRequest = {
  sessionId: string
  modifications: {
    deletions?: number[]
    edits?: { turn: number; newContent: string }[]
    compressions?: { start: number; end: number; reason: string }[]
  }
}

export type ApplyDoctorModificationsResponse = {
  sessionId: string
  result: {
    appliedDeletions?: number[]
    appliedEdits?: { turn: number; newContent: string }[]
    appliedCompressions?: { start: number; end: number; summary: string }[]
    status: string
    reason?: string
  }
}

export const applyDoctorModifications = async (
  data: ApplyDoctorModificationsRequest
): Promise<ApplyDoctorModificationsResponse> =>
  client.post<ApplyDoctorModificationsResponse>('/doctor', {
    body: data
  })
