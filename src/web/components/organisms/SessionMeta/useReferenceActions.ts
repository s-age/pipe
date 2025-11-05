import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { getSession, SessionDetail } from '@/lib/api/session/getSession'

export const useReferenceActions = (
  sessionDetail: SessionDetail | null,
  setSessionDetail: (data: SessionDetail | null) => void,
  setError: (err: string | null) => void,
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
  const handleUpdateReferencePersist = useCallback(
    async (sessionId: string, index: number, persist: boolean): Promise<void> => {
      try {
        await editReferencePersist(sessionId, index, persist)
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference persist state.')
      }
    },
    [setSessionDetail, setError, refreshSessions],
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        const data = await getSession(sessionId)
        setSessionDetail(data.session)
        if (refreshSessions) await refreshSessions()
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference TTL.')
      }
    },
    [setSessionDetail, setError, refreshSessions],
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
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to update reference disabled state.')
      }
    },
    [sessionDetail, setSessionDetail, setError, refreshSessions],
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  }
}
