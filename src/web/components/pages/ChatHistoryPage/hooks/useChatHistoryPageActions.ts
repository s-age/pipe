import { useCallback } from 'react'

import { getChatHistory } from '@/lib/api/bff/getChatHistory'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'
import type { Actions } from '@/stores/useChatHistoryStore'
import type { SessionNode, SessionPair } from '@/types/session'
import { isSessionPair } from '@/types/session'

type UseChatHistoryPageActionsProperties = {
  currentSessionId: string | null
  refreshSessions: Actions['refreshSessions']
}

export const useChatHistoryPageActions = ({
  currentSessionId,
  refreshSessions
}: UseChatHistoryPageActionsProperties): {
  onRefresh: (sessionId?: string) => Promise<void>
} => {
  const onRefresh = useCallback(
    async (sessionId?: string): Promise<void> => {
      const idToUse = sessionId ?? currentSessionId
      const data = await getChatHistory(idToUse || undefined)
      // `session_tree` may be either legacy flat pairs ([id, overview])
      // or hierarchical nodes. Normalize to a flat SessionOverview[]
      const sessionTree = data.session_tree as SessionNode[]

      const flattenPairs = (pairs: SessionPair[]): SessionOverview[] =>
        pairs.map(([id, session]) => ({ ...session, session_id: id }))

      // Preserve hierarchical nodes when backend returns a tree; otherwise
      // normalize legacy pair format to flat `SessionOverview[]`.
      if (Array.isArray(sessionTree) && sessionTree.length > 0) {
        const first = sessionTree[0]

        if (isSessionPair(first)) {
          const normalized = flattenPairs(sessionTree as SessionPair[])
          refreshSessions(data.current_session, normalized)
        } else {
          // Keep hierarchical nodes intact so the UI can render a tree.
          refreshSessions(data.current_session, sessionTree as SessionTreeNode[])
        }
      } else {
        // No sessions returned: ensure session detail is updated but don't touch sessions
        refreshSessions(data.current_session)
      }
    },
    [currentSessionId, refreshSessions]
  )

  return { onRefresh }
}
