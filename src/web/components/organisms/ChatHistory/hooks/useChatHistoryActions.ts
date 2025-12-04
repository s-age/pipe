import { useCallback } from 'react'

import { deleteSession } from '@/lib/api/session/deleteSession'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'
import { addToast } from '@/stores/useToastStore'

type UseChatHistoryActionsProperties = {
  currentSessionId: string | null
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

type UseChatHistoryActionsReturn = {
  deleteSessionAction: (sessionId: string) => Promise<void>
  refreshSession: () => Promise<void>
}

export const useChatHistoryActions = ({
  currentSessionId,
  refreshSessionsInStore
}: UseChatHistoryActionsProperties): UseChatHistoryActionsReturn => {
  // Session actions
  const deleteSessionAction = useCallback(async (sessionId: string): Promise<void> => {
    try {
      await deleteSession(sessionId)
      addToast({ status: 'success', title: 'Session deleted successfully' })
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to delete session.'
      })
    }
  }, [])

  const refreshSession = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return

    try {
      const fetchedSessionDetailResponse = await getSession(currentSessionId)
      const fetchedSessionTree = await getSessionTree()
      let newSessions: SessionOverview[]
      if (fetchedSessionTree.session_tree) {
        // hierarchical nodes — flatten for refreshSessionsInStore
        const flatten: SessionOverview[] = []
        const walk = (nodes: SessionTreeNode[]): void => {
          for (const n of nodes) {
            const overview = (n.overview || {}) as Partial<SessionOverview>
            flatten.push({
              session_id: n.session_id,
              purpose: (overview.purpose as string) || '',
              background: (overview.background as string) || '',
              roles: (overview.roles as string[]) || [],
              procedure: (overview.procedure as string) || '',
              artifacts: (overview.artifacts as string[]) || [],
              multi_step_reasoning_enabled: !!overview.multi_step_reasoning_enabled,
              token_count: (overview.token_count as number) || 0,
              last_updated_at: (overview.last_updated_at as string) || ''
            })
            if (n.children && n.children.length) walk(n.children)
          }
        }
        walk(fetchedSessionTree.session_tree)
        newSessions = flatten
      } else {
        newSessions = fetchedSessionTree.sessions.map(([id, session]) => ({
          ...session,
          session_id: id
        }))
      }
      refreshSessionsInStore(fetchedSessionDetailResponse.session, newSessions)
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to refresh session.'
      })
    }
  }, [currentSessionId, refreshSessionsInStore])

  return {
    // Session actions
    deleteSessionAction,
    refreshSession
  }
}
