import { useCallback } from 'react'

import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

export type UseSessionItemActionsReturn = {
  loadSession: (sessionId: string) => Promise<SessionDetail>
}

export const useSessionItemActions = (): UseSessionItemActionsReturn => {
  const loadSession = useCallback(async (sessionId: string): Promise<SessionDetail> => {
    try {
      const sessionDetail = await getSession(sessionId)
      emitToast.success('Session loaded successfully')

      return sessionDetail.session
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to load session data.')
      throw error
    }
  }, [])

  return { loadSession }
}
