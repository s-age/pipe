import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'

export const useReferenceActions = (
  sessionDetail: SessionDetail | null,
  setSessionDetail: (data: SessionDetail | null) => void,
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
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update reference persist state.',
        )
      }
    },
    [setSessionDetail, refreshSessions, toast],
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    [setSessionDetail, refreshSessions, toast],
  )

  const handleUpdateReferenceDisabled = useCallback(
    async (sessionId: string, index: number, disabled: boolean): Promise<void> => {
      if (!sessionDetail) return
      try {
        const newReferences = [...sessionDetail.references]
        newReferences[index] = { ...newReferences[index], disabled }
        await editReferences(sessionId, newReferences)
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update reference disabled state.',
        )
      }
    },
    [sessionDetail, setSessionDetail, refreshSessions, toast],
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  }
}
