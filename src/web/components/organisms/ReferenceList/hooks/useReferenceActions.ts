import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import type { Reference } from '@/types/reference'

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
  handleAddReference: (sessionId: string, path: string) => Promise<void>
} => {
  const toast = useToast()
  const handleUpdateReferencePersist = useCallback(
    async (
      sessionId: string | null,
      index: number,
      persist: boolean
    ): Promise<void> => {
      if (!sessionId) return

      try {
        await editReferencePersist(sessionId, index, persist)
        // Prefer refreshSessions to allow parent to re-fetch canonical session state
        if (refreshSessions) await refreshSessions()

        toast.success('Reference persist state updated successfully')
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update reference persist state.'
        )
      }
    },
    [toast, refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string | null, index: number, ttl: number): Promise<void> => {
      if (!sessionId) return

      try {
        await editReferenceTtl(sessionId, index, ttl)
        if (refreshSessions) await refreshSessions()

        toast.success('Reference TTL updated successfully')
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    [toast, refreshSessions]
  )

  const handleAddReference = useCallback(
    async (sessionId: string, path: string): Promise<void> => {
      if (!sessionId) return
      try {
        const newReference: Reference = {
          path,
          disabled: false,
          persist: false,
          ttl: 3
        }
        // const newReferences = [...sessionDetail.references, newReference]
        const newReferences = [newReference] // --- IGNORE ---
        await editReferences(sessionId, newReferences)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to add reference.')
      }
    },
    // [sessionDetail, toast, refreshSessions]
    [toast, refreshSessions]
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleAddReference
  }
}
