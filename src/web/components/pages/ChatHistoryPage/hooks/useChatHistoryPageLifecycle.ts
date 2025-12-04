import { useCallback } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getChatHistory } from '@/lib/api/bff/getChatHistory'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import type { Actions, State } from '@/stores/useChatHistoryStore'
import { addToast } from '@/stores/useToastStore'
import type { SessionPair } from '@/types/session'
import { isSessionPair } from '@/types/session'

type UseSessionLoaderProperties = {
  state: State
  actions: Actions
}

export const useSessionLoader = ({
  state,
  actions
}: UseSessionLoaderProperties): void => {
  const {
    sessionTree: { currentSessionId }
  } = state
  const {
    setSessions,
    setCurrentSessionId,
    setSessionDetail,
    setRoleOptions,
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
      if (Array.isArray(data.session_tree) && data.session_tree.length > 0) {
        const first = data.session_tree[0]

        if (isSessionPair(first)) {
          // legacy flat [id, overview][] pairs
          setSessions(
            (data.session_tree as SessionPair[]).map(([id, session]) => ({
              ...session,
              session_id: id
            }))
          )
        } else {
          // hierarchical nodes
          setSessions(data.session_tree as SessionTreeNode[])
        }
      }

      if (data.current_session) {
        setSessionDetail(data.current_session)
        setRoleOptions(data.role_options || [])
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
