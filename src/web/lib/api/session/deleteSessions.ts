import { client } from '../client'

export type DeleteSessionsRequest = {
  session_ids: string[]
}

export type DeleteSessionsResponse = {
  message: string
  deleted_count: number
  total_requested: number
}

export const deleteSessions = async (
  request: DeleteSessionsRequest
): Promise<DeleteSessionsResponse> =>
  client.post<DeleteSessionsResponse>('/sessions/delete', {
    body: request
  })
