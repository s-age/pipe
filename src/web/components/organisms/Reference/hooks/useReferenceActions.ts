import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/meta/editReferencePersist'
import { editReferenceTtl } from '@/lib/api/meta/editReferenceTtl'
import { toggleReferenceDisabled } from '@/lib/api/meta/toggleReferenceDisabled'
import { addToast } from '@/stores/useToastStore'

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
        addToast({
          status: 'success',
          title: 'Reference persist state updated successfully'
        })
        // Prefer refreshSessions to allow parent to re-fetch canonical session state
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update reference persist state.'
        })
      }
    },
    [refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string | null, index: number, ttl: number): Promise<void> => {
      if (!sessionId) return

      try {
        await editReferenceTtl(sessionId, index, ttl)
        addToast({ status: 'success', title: 'Reference TTL updated successfully' })
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update reference TTL.'
        })
      }
    },
    [refreshSessions]
  )

  const handleToggleReferenceDisabled = useCallback(
    async (sessionId: string | null, index: number): Promise<void> => {
      if (!sessionId) return

      try {
        await toggleReferenceDisabled(sessionId, index)
        addToast({
          status: 'success',
          title: 'Reference disabled state updated successfully'
        })
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title:
            (error as Error).message || 'Failed to update reference disabled state.'
        })
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
