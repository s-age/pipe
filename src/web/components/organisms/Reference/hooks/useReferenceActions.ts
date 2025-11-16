import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { toggleReferenceDisabled } from '@/lib/api/session/toggleReferenceDisabled'
import { emitToast } from '@/lib/toastEvents'

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

      try {
        await editReferencePersist(sessionId, index, persist)
        emitToast.success('Reference persist state updated successfully')
        // Prefer refreshSessions to allow parent to re-fetch canonical session state
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update reference persist state.'
        )
      }
    },
    [refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string | null, index: number, ttl: number): Promise<void> => {
      if (!sessionId) return

      try {
        await editReferenceTtl(sessionId, index, ttl)
        emitToast.success('Reference TTL updated successfully')
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    [refreshSessions]
  )

  const handleToggleReferenceDisabled = useCallback(
    async (sessionId: string | null, index: number): Promise<void> => {
      if (!sessionId) return

      try {
        await toggleReferenceDisabled(sessionId, index)
        emitToast.success('Reference disabled state updated successfully')
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update reference disabled state.'
        )
      }
    },
    [refreshSessions]
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  }
}
