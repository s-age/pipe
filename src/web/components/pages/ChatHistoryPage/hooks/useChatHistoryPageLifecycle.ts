import { useCallback } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getSessionDashboard } from '@/lib/api/bff/getSessionDashboard'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { Actions, State } from '@/stores/useChatHistoryStore'
import { addToast } from '@/stores/useToastStore'

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
  const { setSessions, setCurrentSessionId, setSessionDetail, setRoleOptions } = actions

  const loadSessions = useCallback(async (): Promise<void> => {
    try {
      // Extract session ID from URL if not already set
      const pathParts = window.location.pathname.split('/')
      const urlSessionId = pathParts[pathParts.length - 1]
      const shouldSetInitialId =
        urlSessionId &&
        urlSessionId !== 'session' &&
        urlSessionId !== '' &&
        !currentSessionId

      if (shouldSetInitialId) {
        setCurrentSessionId(urlSessionId)
      }

      // Use BFF endpoint if we have a session ID, otherwise use session tree endpoint
      const sessionIdToLoad = shouldSetInitialId ? urlSessionId : currentSessionId

      if (sessionIdToLoad) {
        const data = await getSessionDashboard(sessionIdToLoad)
        setSessions(
          data.session_tree.map(([id, session]) => ({
            ...session,
            session_id: id
          }))
        )
        setSessionDetail(data.current_session)
        setRoleOptions(data.role_options)
      } else {
        const fetchedSessions = await getSessionTree()
        setSessions(
          fetchedSessions.sessions.map(([id, session]) => ({
            ...session,
            session_id: id
          }))
        )
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
    setRoleOptions
  ])

  useInitialLoading(loadSessions)
}
