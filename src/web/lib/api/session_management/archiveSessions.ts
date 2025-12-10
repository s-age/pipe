import { client } from '../client'

export type ArchiveSessionsRequest = {
  sessionIds: string[]
}

export type ArchiveSessionsResponse = {
  message: string
  archivedCount: number
  totalRequested: number
}

export const archiveSessions = async (
  request: ArchiveSessionsRequest
): Promise<ArchiveSessionsResponse> =>
  client.post<ArchiveSessionsResponse>('/session_management/archives', {
    body: request
  })
