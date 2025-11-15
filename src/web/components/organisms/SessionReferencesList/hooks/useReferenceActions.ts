import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'

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
      await editReferencePersist(sessionId, index, persist)
      const data = await getSession(sessionId)
      setSessionDetail(data.session)
      if (refreshSessions) await refreshSessions()
    },
    [setSessionDetail, refreshSessions]
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      await editReferenceTtl(sessionId, index, ttl)
      const data = await getSession(sessionId)
      setSessionDetail(data.session)
      if (refreshSessions) await refreshSessions()
    },
    [setSessionDetail, refreshSessions]
  )

  const handleUpdateReferenceDisabled = useCallback(
    async (sessionId: string, index: number, disabled: boolean): Promise<void> => {
      if (!sessionDetail) return
      const newReferences = [...sessionDetail.references]
      newReferences[index] = { ...newReferences[index], disabled }
      await editReferences(sessionId, newReferences)
      const data = await getSession(sessionId)
      setSessionDetail(data.session)
      if (refreshSessions) await refreshSessions()
    },
    [sessionDetail, setSessionDetail, refreshSessions]
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled
  }
}
