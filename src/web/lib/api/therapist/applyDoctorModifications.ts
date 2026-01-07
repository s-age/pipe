import { client } from '../client'

export type ApplyDoctorModificationsRequest = {
  modifications: {
    compressions?: { end: number; reason: string; start: number }[]
    deletions?: number[]
    edits?: { newContent: string; turn: number }[]
  }
  sessionId: string
}

export type ApplyDoctorModificationsResponse = {
  result: {
    status: string
    appliedCompressions?: { end: number; start: number; summary: string }[]
    appliedDeletions?: number[]
    appliedEdits?: { newContent: string; turn: number }[]
    reason?: string
  }
  sessionId: string
}

export const applyDoctorModifications = async (
  data: ApplyDoctorModificationsRequest
): Promise<ApplyDoctorModificationsResponse> =>
  client.post<ApplyDoctorModificationsResponse>('/doctor', {
    body: data
  })
