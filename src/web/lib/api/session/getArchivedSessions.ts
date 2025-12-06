import { client } from '../client'
import type { SessionOverview } from '../sessionTree/getSessionTree'

type ArchivedSession = {
  sessionId: string
  filePath: string
  purpose: string | null
  deletedAt: string | null
}

export const getArchivedSessions = async (): Promise<SessionOverview[]> => {
  const response = await client.get<{ sessions: ArchivedSession[] }>(
    '/sessions/archives'
  )

  return response.sessions.map((s) => ({
    sessionId: s.sessionId,
    purpose: s.purpose || '',
    background: '',
    roles: [],
    procedure: '',
    artifacts: [],
    multiStepReasoningEnabled: false,
    tokenCount: 0,
    lastUpdatedAt: '',
    deletedAt: s.deletedAt || ''
  }))
}
