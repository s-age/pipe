import { useEffect } from 'react'

import { getSession } from '@/lib/api/session/getSession'
import type { Actions, State } from '@/stores/useChatHistoryStore'

type UseSessionDetailLoaderProperties = {
  state: State
  actions: Actions
}

export const useSessionDetailLoader = ({
  state,
  actions,
}: UseSessionDetailLoaderProperties): void => {
  const {
    sessionTree: { currentSessionId },
  } = state
  const { setSessionDetail, setError } = actions

  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSession(currentSessionId)
          setSessionDetail(data.session)
          setError(null)
        } catch (error: unknown) {
          setError((error as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionDetail(null)
      }
    }
    loadSessionDetail()
  }, [currentSessionId, setSessionDetail, setError])
}
