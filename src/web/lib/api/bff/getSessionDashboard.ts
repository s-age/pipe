import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { RoleOption } from '../roles/getRoles'
import type { SessionDetail } from '../session/getSession'
import type { SessionOverview } from '../sessionTree/getSessionTree'

export type SessionDashboardResponse = {
  session_tree: [string, SessionOverview][]
  current_session: SessionDetail
  settings: Settings
  role_options: RoleOption[]
}

export const getSessionDashboard = async (
  sessionId: string
): Promise<SessionDashboardResponse> =>
  client.get<SessionDashboardResponse>(`/bff/session-dashboard/${sessionId}`)
