import { useEffect } from 'react'

import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { Actions, State } from '@/stores/useChatHistoryStore'

type UseSessionLoaderProperties = {
  state: State
  actions: Actions
}

export const useSessionLoader = ({
  state,
  actions,
}: UseSessionLoaderProperties): void => {
  const {
    sessionTree: { currentSessionId },
  } = state
  const { setSessions, setCurrentSessionId, setError } = actions

  useEffect(() => {
    const loadSessions = async (): Promise<void> => {
      try {
        const fetchedSessions = await getSessionTree()
        setSessions(
          fetchedSessions.sessions.map(([id, session]) => ({
            ...session,
            session_id: id,
          })),
        )
        const pathParts = window.location.pathname.split('/')
        const id = pathParts[pathParts.length - 1]
        if (id && id !== 'session' && id !== '' && !currentSessionId) {
          setCurrentSessionId(id)
        }
        setError(null)
      } catch (error: unknown) {
        setError((error as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
  }, [setSessions, setCurrentSessionId, setError, currentSessionId])
}
