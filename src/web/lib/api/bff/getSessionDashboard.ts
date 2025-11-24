import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { RoleOption } from '../roles/getRoles'
import type { SessionDetail } from '../session/getSession'
import type { SessionOverview, SessionTreeNode } from '../sessionTree/getSessionTree'

export type SessionDashboardResponse = {
  // `session_tree` may be either an array of [id, overview] pairs (legacy)
  // or an array of hierarchical nodes produced by the backend.
  session_tree: [string, SessionOverview][] | SessionTreeNode[]
  current_session: SessionDetail
  settings: Settings
  role_options: RoleOption[]
}

export const getSessionDashboard = async (
  sessionId: string
): Promise<SessionDashboardResponse> =>
  client.get<SessionDashboardResponse>(`/bff/session-dashboard/${sessionId}`)
