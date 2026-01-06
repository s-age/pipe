import { client } from '../client'
import type { SessionOverview, SessionTreeNode } from '../sessionTree/getSessionTree'

export type SessionManagementDashboardResponse = {
  archives: SessionOverview[]
  sessionTree: SessionTreeNode[]
}

export const getSessionManagement =
  async (): Promise<SessionManagementDashboardResponse> =>
    client.get<SessionManagementDashboardResponse>('/bff/session_management')
