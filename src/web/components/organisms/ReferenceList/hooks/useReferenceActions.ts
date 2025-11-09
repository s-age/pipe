import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useReferenceActions = (
  sessionDetail: SessionDetail | null,
  refreshSessions?: () => Promise<void>,
): {
  handleUpdateReferencePersist: (
    sessionId: string,
    index: number,
    persist: boolean,
  ) => Promise<void>
  handleUpdateReferenceTtl: (
    sessionId: string,
    index: number,
    ttl: number,
  ) => Promise<void>
  handleUpdateReferenceDisabled: (
    sessionId: string,
    index: number,
    disabled: boolean,
  ) => Promise<void>
} => {
  const toast = useToast()
  const handleUpdateReferencePersist = useCallback(
    async (sessionId: string, index: number, persist: boolean): Promise<void> => {
      try {
        await editReferencePersist(sessionId, index, persist)
        // Prefer refreshSessions to allow parent to re-fetch canonical session state
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update reference persist state.',
        )
      }
    },
    [toast, refreshSessions],
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    [toast, refreshSessions],
  )

  const handleUpdateReferenceDisabled = useCallback(
    async (sessionId: string, index: number, disabled: boolean): Promise<void> => {
      if (!sessionDetail) return
      try {
        const newReferences = [...sessionDetail.references]
        newReferences[index] = { ...newReferences[index], disabled }
        await editReferences(sessionId, newReferences)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update reference disabled state.',
        )
      }
    },
    [sessionDetail, toast, refreshSessions],
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  }
}
