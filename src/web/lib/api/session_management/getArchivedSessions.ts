import { client } from '../client'
import type { SessionOverview } from '../sessionTree/getSessionTree'

type ArchivedSession = {
  deletedAt: string | null
  filePath: string
  purpose: string | null
  sessionId: string
}

export const getArchivedSessions = async (): Promise<SessionOverview[]> => {
  const response = await client.get<{ sessions: ArchivedSession[] }>(
    '/session_management/archives'
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
    deletedAt: s.deletedAt || '',
    filePath: s.filePath
  }))
}
