import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { RoleOption } from '../roles/getRoles'
import type { SessionDetail } from '../session/getSession'
import type { SessionOverview, SessionTreeNode } from '../sessionTree/getSessionTree'

export type ChatHistoryResponse = {
  sessions: [string, SessionOverview][]
  session_tree: SessionTreeNode[]
  settings: Settings
  current_session?: SessionDetail
  role_options?: RoleOption[]
}

export const getChatHistory = async (
  sessionId?: string
): Promise<ChatHistoryResponse> => {
  const url = sessionId
    ? `/bff/chat_history?session_id=${encodeURIComponent(sessionId)}`
    : '/bff/chat_history'

  return client.get<ChatHistoryResponse>(url)
}
