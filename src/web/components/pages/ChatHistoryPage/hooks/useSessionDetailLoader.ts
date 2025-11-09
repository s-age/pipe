import { useEffect } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
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
  const { setSessionDetail } = actions
  const toast = useToast()

  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSession(currentSessionId)
          setSessionDetail(data.session)
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
