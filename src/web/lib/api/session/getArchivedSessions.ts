import { client } from '../client'
import type { SessionOverview } from '../sessionTree/getSessionTree'

type ArchivedSession = {
  session_id: string
  file_path: string
  purpose: string | null
  deleted_at: string | null
}

export const getArchivedSessions = async (): Promise<SessionOverview[]> => {
  const response = await client.get<{ sessions: ArchivedSession[] }>(
    '/sessions/archives'
  )

  return response.sessions.map((s) => ({
    session_id: s.session_id,
    purpose: s.purpose || '',
    background: '',
    roles: [],
    procedure: '',
    artifacts: [],
    multi_step_reasoning_enabled: false,
    token_count: 0,
    last_updated_at: '',
    deleted_at: s.deleted_at || ''
  }))
}
