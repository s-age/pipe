import { client } from '../client'

export type DeleteArchivedSessionsRequest = {
  sessionIds: string[]
}

export type DeleteArchivedSessionsResponse = {
  message: string
  deletedCount: number
  totalRequested: number
}

export const deleteArchivedSessions = async (
  request: DeleteArchivedSessionsRequest
): Promise<DeleteArchivedSessionsResponse> =>
  client.delete<DeleteArchivedSessionsResponse>('/sessions/archives', {
    body: request
  })
