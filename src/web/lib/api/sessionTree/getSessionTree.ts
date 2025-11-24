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

export type SessionTreeNode = {
  session_id: string
  overview: Record<string, unknown>
  children: SessionTreeNode[]
}

export const getSessionTree = async (): Promise<{
  sessions: [string, SessionOverview][]
  session_tree?: SessionTreeNode[]
}> =>
  client.get<{
    sessions: [string, SessionOverview][]
    session_tree?: SessionTreeNode[]
  }>('/session_tree')
