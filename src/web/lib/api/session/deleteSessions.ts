import { client } from '../client'

export type DeleteSessionsRequest = {
  sessionIds: string[]
}

export type DeleteSessionsResponse = {
  message: string
  deletedCount: number
  totalRequested: number
}

export const deleteSessions = async (
  request: DeleteSessionsRequest
): Promise<DeleteSessionsResponse> =>
  client.post<DeleteSessionsResponse>('/sessions/delete', {
    body: request
  })
