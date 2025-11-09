import { client } from '../client'
import type { SessionDetail } from '../session/getSession'
import type { SessionOverview } from '../sessionTree/getSessionTree'
import type { Settings } from '../settings/getSettings'

export type SessionDashboardResponse = {
  session_tree: [string, SessionOverview][]
  current_session: SessionDetail
  settings: Settings
}

export const getSessionDashboard = async (
  sessionId: string,
): Promise<SessionDashboardResponse> =>
  client.get<SessionDashboardResponse>(`/bff/session-dashboard/${sessionId}`)
