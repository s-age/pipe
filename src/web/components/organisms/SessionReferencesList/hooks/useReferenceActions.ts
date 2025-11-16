import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

export const useReferenceActions = (
  sessionDetail: SessionDetail | null,
  setSessionDetail: (data: SessionDetail | null) => void,
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
  handleUpdateReferenceDisabled: (
    sessionId: string,
    index: number,
    disabled: boolean
  ) => Promise<void>
} => {
  const handleUpdateReferencePersist = useCallback(
    async (sessionId: string, index: number, persist: boolean): Promise<void> => {
      try {
        await editReferencePersist(sessionId, index, persist)
        emitToast.success('Reference persist state updated successfully')
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update reference persist state.'
        )
      }
    },
    [setSessionDetail, refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        emitToast.success('Reference TTL updated successfully')
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to update reference TTL.')
      }
    },
    [setSessionDetail, refreshSessions]
  )

  const handleUpdateReferenceDisabled = useCallback(
    async (sessionId: string, index: number, disabled: boolean): Promise<void> => {
      if (!sessionDetail) return
      const newReferences = [...sessionDetail.references]
      newReferences[index] = { ...newReferences[index], disabled }
      try {
        await editReferences(sessionId, newReferences)
        emitToast.success('Reference disabled state updated successfully')
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update reference disabled state.'
        )
      }
    },
    [sessionDetail, setSessionDetail, refreshSessions]
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled
  }
}
