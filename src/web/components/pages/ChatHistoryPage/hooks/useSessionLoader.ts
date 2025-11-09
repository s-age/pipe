import { useEffect } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { getSessionDashboard } from '@/lib/api/bff/getSessionDashboard'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { Actions, State } from '@/stores/useChatHistoryStore'

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
  const { setSessions, setCurrentSessionId, setSessionDetail } = actions
  const toast = useToast()

  useEffect(() => {
    const loadSessions = async (): Promise<void> => {
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
        toast.failure((error as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Load session detail when currentSessionId changes
  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSessionDashboard(currentSessionId)
          setSessionDetail(data.current_session)
        } catch (error: unknown) {
          toast.failure((error as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionDetail(null)
      }
    }
    loadSessionDetail()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentSessionId])
}
