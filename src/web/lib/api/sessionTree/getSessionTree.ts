import { client } from '../client'

export type SessionOverview = {
  artifacts: string[]
  background: string
  lastUpdatedAt: string
  multiStepReasoningEnabled: boolean
  procedure: string
  purpose: string
  roles: string[]
  sessionId: string
  tokenCount: number
  deletedAt?: string
  filePath?: string
}

export type SessionTreeNode = {
  children: SessionTreeNode[]
  overview: SessionOverview
  sessionId: string
}

export const getSessionTree = async (): Promise<{
  sessions: [string, SessionOverview][]
  sessionTree?: SessionTreeNode[]
}> =>
  client.get<{
    sessions: [string, SessionOverview][]
    sessionTree?: SessionTreeNode[]
  }>('/session_tree')
