import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { toggleReferenceDisabled } from '@/lib/api/session/toggleReferenceDisabled'

export const useReferenceActions = (
  refreshSessions?: () => Promise<void>
): {
  handleUpdateReferencePersist: (
    sessionId: string,
    index: number,
    persist: boolean
  ) => Promise<void>
  handleUpdateReferenceTtl: (
    sessionId: string,
    index: number,
    ttl: number
  ) => Promise<void>
  handleToggleReferenceDisabled: (sessionId: string, index: number) => Promise<void>
} => {
  const handleUpdateReferencePersist = useCallback(
    async (
      sessionId: string | null,
      index: number,
      persist: boolean
    ): Promise<void> => {
      if (!sessionId) return

      await editReferencePersist(sessionId, index, persist)
      // Prefer refreshSessions to allow parent to re-fetch canonical session state
      if (refreshSessions) await refreshSessions()
    },
    [refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string | null, index: number, ttl: number): Promise<void> => {
      if (!sessionId) return

      await editReferenceTtl(sessionId, index, ttl)
      if (refreshSessions) await refreshSessions()
    },
    [refreshSessions]
  )

  const handleToggleReferenceDisabled = useCallback(
    async (sessionId: string | null, index: number): Promise<void> => {
      if (!sessionId) return

      await toggleReferenceDisabled(sessionId, index)
      if (refreshSessions) await refreshSessions()
    },
    [refreshSessions]
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  }
}
