import { client } from '../client'

export type SessionOverview = {
  session_id: string
  purpose: string
  background: string
  roles: string[]
  procedure: string
  artifacts: string[]
  multi_step_reasoning_enabled: boolean
  token_count: number
  last_update: string
}

export const getSessions = async (): Promise<{
  sessions: [string, SessionOverview][]
}> => client.get<{ sessions: [string, SessionOverview][] }>(`/sessions`)
