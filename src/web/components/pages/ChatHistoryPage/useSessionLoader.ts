import { useEffect } from 'react'

import { getSessions } from '@/lib/api/sessions/getSessions'
import { Actions, State } from '@/stores/useChatHistoryStore'

type UseSessionLoaderProps = {
  state: State
  actions: Actions
}

export const useSessionLoader = ({ state, actions }: UseSessionLoaderProps): void => {
  const {
    sessionTree: { currentSessionId },
  } = state
  const { setSessions, setCurrentSessionId, setError } = actions

  useEffect(() => {
    const loadSessions = async (): Promise<void> => {
      try {
        const fetchedSessions = await getSessions()
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
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
  }, [setSessions, setCurrentSessionId, setError, currentSessionId])
}
