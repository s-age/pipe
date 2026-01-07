import { client } from '../client'

export type DeleteSessionsRequest = {
  sessionIds: string[]
}

export type DeleteSessionsResponse = {
  deletedCount: number
  message: string
  totalRequested: number
}

export const deleteSessions = async (
  request: DeleteSessionsRequest
): Promise<DeleteSessionsResponse> =>
  client.delete<DeleteSessionsResponse>('/session_management/sessions', {
    body: request
  })
