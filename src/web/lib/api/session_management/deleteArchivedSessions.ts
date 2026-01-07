import { client } from '../client'

export type DeleteArchivedSessionsRequest = {
  filePaths?: string[]
  sessionIds?: string[]
}

export type DeleteArchivedSessionsResponse = {
  deletedCount: number
  message: string
  totalRequested: number
}

export const deleteArchivedSessions = async (
  request: DeleteArchivedSessionsRequest
): Promise<DeleteArchivedSessionsResponse> =>
  client.delete<DeleteArchivedSessionsResponse>('/session_management/archives', {
    body: request
  })
