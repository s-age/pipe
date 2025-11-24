import { client as apiClient } from '@/lib/api/client'

export type SearchResult = {
  session_id: string
  title: string
}

export type SearchSessionsRequest = {
  query: string
}

export type SearchSessionsResponse = {
  results: SearchResult[]
}

export const searchSessions = async (
  payload: SearchSessionsRequest
): Promise<SearchSessionsResponse> =>
  apiClient.post<SearchSessionsResponse>('/search', { body: payload })
