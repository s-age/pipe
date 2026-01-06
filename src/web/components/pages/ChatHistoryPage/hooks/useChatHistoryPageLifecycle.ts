import { useCallback } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getChatHistory } from '@/lib/api/bff/getChatHistory'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import type { Actions, State } from '@/stores/useChatHistoryStore'
import { addToast } from '@/stores/useToastStore'
import type { SessionPair } from '@/types/session'
import { isSessionPair } from '@/types/session'

type UseChatHistoryPageLifecycleProperties = {
  actions: Actions
  state: State
}

export const useChatHistoryPageLifecycle = ({
  actions,
  state
}: UseChatHistoryPageLifecycleProperties): void => {
  const {
    sessionTree: { currentSessionId }
  } = state
  const {
    setCurrentSessionId,
    setRoleOptions,
    setSessionDetail,
    setSessions,
    updateSettings
  } = actions

  const loadSessions = useCallback(async (): Promise<void> => {
    try {
      // Extract session ID from URL if not already set. Support session IDs
      // that may contain slashes (e.g. parent/child). We take the full
      // path after the `/session/` prefix instead of only the last segment.
      const pathname = window.location.pathname || ''
      let urlSessionId = ''
      if (pathname.startsWith('/session/')) {
        urlSessionId = pathname.substring('/session/'.length)
      }

      const shouldSetInitialId =
        urlSessionId &&
        urlSessionId !== 'session' &&
        urlSessionId !== '' &&
        !currentSessionId

      if (shouldSetInitialId) {
        setCurrentSessionId(urlSessionId)
      }

      // Always use BFF endpoint for chat history
      const sessionIdToLoad = shouldSetInitialId ? urlSessionId : currentSessionId

      const data = await getChatHistory(sessionIdToLoad || undefined)

      updateSettings(data.settings || {})

      // `session_tree` from server may be hierarchical (SessionTreeNode[]) or flat pairs.
      if (Array.isArray(data.sessionTree) && data.sessionTree.length > 0) {
        const first = data.sessionTree[0]

        if (isSessionPair(first)) {
          // legacy flat [id, overview][] pairs
          setSessions(
            (data.sessionTree as unknown as SessionPair[]).map(([id, session]) => ({
              ...session,
              sessionId: id
            }))
          )
        } else {
          // hierarchical nodes
          setSessions(data.sessionTree as SessionTreeNode[])
        }
      }

      if (data.currentSession) {
        setSessionDetail(data.currentSession)
        setRoleOptions(data.roleOptions || [])
      } else {
        setSessionDetail(null)
      }
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to load sessions.'
      })
    }
  }, [
    currentSessionId,
    setCurrentSessionId,
    setSessions,
    setSessionDetail,
    setRoleOptions,
    updateSettings
  ])

  useInitialLoading(loadSessions)
}
