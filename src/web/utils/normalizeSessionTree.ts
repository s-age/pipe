import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

/**
 * Normalize session tree data into a flat array of SessionOverview
 * Handles both hierarchical tree nodes and flat session arrays
 */
export const normalizeSessionTree = (sessionTreeData: {
  sessions: Array<[string, SessionOverview]>
  sessionTree?: SessionTreeNode[]
}): SessionOverview[] => {
  if (sessionTreeData.sessionTree) {
    // Hierarchical nodes - flatten for display
    const flatten: SessionOverview[] = []
    const walk = (nodes: SessionTreeNode[]): void => {
      for (const n of nodes) {
        const overview = (n.overview || {}) as Partial<SessionOverview>
        flatten.push({
          sessionId: n.sessionId,
          purpose: (overview.purpose as string) || '',
          background: (overview.background as string) || '',
          roles: (overview.roles as string[]) || [],
          procedure: (overview.procedure as string) || '',
          artifacts: (overview.artifacts as string[]) || [],
          multiStepReasoningEnabled: !!overview.multiStepReasoningEnabled,
          tokenCount: (overview.tokenCount as number) || 0,
          lastUpdatedAt: (overview.lastUpdatedAt as string) || ''
        })
        if (n.children && n.children.length) walk(n.children)
      }
    }
    walk(sessionTreeData.sessionTree)

    return flatten
  } else {
    // Flat array format - convert from tuple to object
    return sessionTreeData.sessions.map(([id, session]: [string, SessionOverview]) => ({
      ...session,
      sessionId: id
    }))
  }
}
