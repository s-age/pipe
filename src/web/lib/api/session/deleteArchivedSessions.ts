import { client } from '../client'

export type DeleteArchivedSessionsRequest = {
  session_ids: string[]
}

export type DeleteArchivedSessionsResponse = {
  message: string
  deleted_count: number
  total_requested: number
}

export const deleteArchivedSessions = async (
  request: DeleteArchivedSessionsRequest
): Promise<DeleteArchivedSessionsResponse> =>
  client.delete<DeleteArchivedSessionsResponse>('/sessions/archives', {
    body: request
  })
