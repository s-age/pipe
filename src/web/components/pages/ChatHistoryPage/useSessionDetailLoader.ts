import { useEffect } from 'react'

import { getSession } from '@/lib/api/session/getSession'
import { Actions, State } from '@/stores/useChatHistoryStore'

type UseSessionDetailLoaderProps = {
  state: State
  actions: Actions
}

export const useSessionDetailLoader = ({
  state,
  actions,
}: UseSessionDetailLoaderProps): void => {
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
        } catch (err: unknown) {
          setError((err as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionDetail(null)
      }
    }
    loadSessionDetail()
  }, [currentSessionId, setSessionDetail, setError])
}
