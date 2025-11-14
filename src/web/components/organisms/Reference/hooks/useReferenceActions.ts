import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { toggleReferenceDisabled } from '@/lib/api/session/toggleReferenceDisabled'
import { emitToast } from '@/lib/toastEvents'

export const useReferenceActions = (): {
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
        // Removed refreshSessions to prevent scroll reset

        emitToast.success('Reference persist state updated successfully')
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update reference persist state.'
        )
      }
    },
    []
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string | null, index: number, ttl: number): Promise<void> => {
      if (!sessionId) return

      try {
        await editReferenceTtl(sessionId, index, ttl)
        // Removed refreshSessions to prevent scroll reset

        emitToast.success('Reference TTL updated successfully')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    []
  )

  const handleToggleReferenceDisabled = useCallback(
    async (sessionId: string | null, index: number): Promise<void> => {
      if (!sessionId) return

      try {
        await toggleReferenceDisabled(sessionId, index)
        // Removed refreshSessions to prevent scroll reset

        emitToast.success('Reference toggled successfully')
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to toggle reference.')
      }
    },
    []
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  }
}
