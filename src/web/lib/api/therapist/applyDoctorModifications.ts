import { client } from '../client'

export type ApplyDoctorModificationsRequest = {
  session_id: string
  modifications: {
    deletions?: number[]
    edits?: { turn: number; suggestion: string }[]
    compressions?: { start: number; end: number; reason: string }[]
  }
}

export type ApplyDoctorModificationsResponse = {
  session_id: string
  result: {
    applied_deletions?: number[]
    applied_edits?: { turn: number; new_content: string }[]
    applied_compressions?: { start: number; end: number; summary: string }[]
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
