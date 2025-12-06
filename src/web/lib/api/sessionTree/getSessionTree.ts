import { client } from '../client'

export type SessionOverview = {
  sessionId: string
  purpose: string
  background: string
  roles: string[]
  procedure: string
  artifacts: string[]
  multiStepReasoningEnabled: boolean
  tokenCount: number
  lastUpdatedAt: string
  deletedAt?: string
}

export type SessionTreeNode = {
  sessionId: string
  overview: SessionOverview
  children: SessionTreeNode[]
}

export const getSessionTree = async (): Promise<{
  sessions: [string, SessionOverview][]
  sessionTree?: SessionTreeNode[]
}> =>
  client.get<{
    sessions: [string, SessionOverview][]
    sessionTree?: SessionTreeNode[]
  }>('/session_tree')
