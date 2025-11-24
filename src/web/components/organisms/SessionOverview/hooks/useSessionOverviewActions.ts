import { useCallback } from 'react'

import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'

export type UseSessionOverviewActionsReturn = {
  loadSession: (sessionId: string) => Promise<SessionDetail>
}

export const useSessionOverviewActions = (): UseSessionOverviewActionsReturn => {
  const loadSession = useCallback(async (sessionId: string): Promise<SessionDetail> => {
    try {
      const sessionDetail = await getSession(sessionId)

      return sessionDetail.session
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to load session data.'
      })
      throw error
    }
  }, [])

  return { loadSession }
}
