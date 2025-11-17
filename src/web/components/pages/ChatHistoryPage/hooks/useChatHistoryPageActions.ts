import { useCallback } from 'react'

import { getSessionDashboard } from '@/lib/api/bff/getSessionDashboard'
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
  onRefresh: () => Promise<void>
} => {
  const onRefresh = useCallback(async (): Promise<void> => {
    if (currentSessionId) {
      const dashBoard = await getSessionDashboard(currentSessionId)
      // `session_tree` may be either legacy flat pairs ([id, overview])
      // or hierarchical nodes. Normalize to a flat SessionOverview[]
      const sessionTree = dashBoard.session_tree as SessionNode[]

      const flattenPairs = (pairs: SessionPair[]): SessionOverview[] =>
        pairs.map(([id, session]) => ({ ...session, session_id: id }))

      const flattenNodes = (nodes: SessionTreeNode[]): SessionOverview[] => {
        const out: SessionOverview[] = []

        const walk = (n: SessionTreeNode): void => {
          const overview = n.overview || {}
          out.push({
            session_id: n.session_id,
            purpose: (overview.purpose as string) || '',
            background: (overview.background as string) || '',
            roles: (overview.roles as string[]) || [],
            procedure: (overview.procedure as string) || '',
            artifacts: (overview.artifacts as string[]) || [],
            multi_step_reasoning_enabled: !!overview.multi_step_reasoning_enabled,
            token_count: (overview.token_count as number) || 0,
            last_update: (overview.last_update as string) || ''
          })

          if (Array.isArray(n.children)) {
            n.children.forEach(walk)
          }
        }

        nodes.forEach(walk)

        return out
      }

      let normalized: SessionOverview[] = []

      if (Array.isArray(sessionTree) && sessionTree.length > 0) {
        const first = sessionTree[0]

        if (isSessionPair(first)) {
          normalized = flattenPairs(sessionTree as SessionPair[])
        } else {
          normalized = flattenNodes(sessionTree as SessionTreeNode[])
        }
      }

      refreshSessions(dashBoard.current_session, normalized)
    }
  }, [currentSessionId, refreshSessions])

  return { onRefresh }
}
