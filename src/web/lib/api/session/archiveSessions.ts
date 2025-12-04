import { client } from '../client'

export type ArchiveSessionsRequest = {
  session_ids: string[]
}

export type ArchiveSessionsResponse = {
  message: string
  archived_count: number
  total_requested: number
}

export const archiveSessions = async (
  request: ArchiveSessionsRequest
): Promise<ArchiveSessionsResponse> =>
  client.post<ArchiveSessionsResponse>('/sessions/archives', {
    body: request
  })
