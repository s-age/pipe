import { client } from '../client'
import type { SessionOverview, SessionTreeNode } from '../sessionTree/getSessionTree'

export type SessionManagementDashboardResponse = {
  session_tree: SessionTreeNode[]
  archives: SessionOverview[]
}

export const getSessionManagement =
  async (): Promise<SessionManagementDashboardResponse> =>
    client.get<SessionManagementDashboardResponse>('/bff/session_management')
