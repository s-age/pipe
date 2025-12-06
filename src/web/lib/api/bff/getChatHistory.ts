import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { RoleOption } from '../roles/getRoles'
import type { SessionDetail } from '../session/getSession'
import type { SessionOverview, SessionTreeNode } from '../sessionTree/getSessionTree'

export type ChatHistoryResponse = {
  sessions: [string, SessionOverview][]
  sessionTree: SessionTreeNode[]
  settings: Settings
  currentSession?: SessionDetail
  roleOptions?: RoleOption[]
}

export const getChatHistory = async (
  sessionId?: string
): Promise<ChatHistoryResponse> => {
  const url = sessionId
    ? `/bff/chat_history?sessionId=${encodeURIComponent(sessionId)}`
    : '/bff/chat_history'

  return client.get<ChatHistoryResponse>(url)
}
