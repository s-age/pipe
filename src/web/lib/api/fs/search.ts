import { client as apiClient } from '@/lib/api/client'

export type SessionSearchResult = {
  sessionId: string
  title: string
}

export type SessionSearchRequest = {
  query: string
}

export type SessionSearchResponse = {
  results: SessionSearchResult[]
}

export const searchSessions = async (
  payload: SessionSearchRequest
): Promise<SessionSearchResponse> =>
  apiClient.post<SessionSearchResponse>('/fs/search', { body: payload })
