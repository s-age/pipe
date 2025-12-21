import { useCallback } from 'react'

import { getChatHistory } from '@/lib/api/bff/getChatHistory'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'
import { addToast } from '@/stores/useToastStore'
import type { SessionNode, SessionPair } from '@/types/session'
import { isSessionPair } from '@/types/session'

type UseChatHistoryPageActionsProperties = {
  currentSessionId: string | null
}

type ChatHistoryData = {
  sessionDetail: SessionDetail | null
  sessions?: SessionOverview[] | SessionTreeNode[]
}

export const useChatHistoryPageActions = ({
  currentSessionId
}: UseChatHistoryPageActionsProperties): {
  fetchChatHistory: (sessionId?: string) => Promise<ChatHistoryData | undefined>
} => {
  const fetchChatHistory = useCallback(
    async (sessionId?: string): Promise<ChatHistoryData | undefined> => {
      try {
        const idToUse = sessionId ?? currentSessionId
        const data = await getChatHistory(idToUse || undefined)
        // `session_tree` may be either legacy flat pairs ([id, overview])
        // or hierarchical nodes. Normalize to a flat SessionOverview[]
        const sessionTree = data.sessionTree as SessionNode[]

        const flattenPairs = (pairs: SessionPair[]): SessionOverview[] =>
          pairs.map(([id, session]) => ({ ...session, sessionId: id }))

        // Preserve hierarchical nodes when backend returns a tree; otherwise
        // normalize legacy pair format to flat `SessionOverview[]`.
        if (Array.isArray(sessionTree) && sessionTree.length > 0) {
          const first = sessionTree[0]

          if (isSessionPair(first)) {
            const normalized = flattenPairs(sessionTree as SessionPair[])

            return {
              sessionDetail: data.currentSession ?? null,
              sessions: normalized
            }
          } else {
            // Keep hierarchical nodes intact so the UI can render a tree.
            return {
              sessionDetail: data.currentSession ?? null,
              sessions: sessionTree as SessionTreeNode[]
            }
          }
        } else {
          // No sessions returned: ensure session detail is updated but don't touch sessions
          return {
            sessionDetail: data.currentSession ?? null
          }
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to refresh sessions'
        })

        return undefined
      }
    },
    [currentSessionId]
  )

  return { fetchChatHistory }
}
