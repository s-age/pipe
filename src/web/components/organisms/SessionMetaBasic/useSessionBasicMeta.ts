import { useState, useCallback } from 'react'

import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionBasicMetaProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
}

export const useSessionBasicMeta = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
}: UseSessionBasicMetaProperties): {
  purpose: string
  setPurpose: React.Dispatch<React.SetStateAction<string>>
  handlePurposeBlur: () => void
  background: string
  setBackground: React.Dispatch<React.SetStateAction<string>>
  handleBackgroundBlur: () => void
  roles: string
  setRoles: React.Dispatch<React.SetStateAction<string>>
  handleRolesBlur: () => void
  procedure: string
  setProcedure: React.Dispatch<React.SetStateAction<string>>
  handleProcedureBlur: () => void
  artifacts: string
  setArtifacts: React.Dispatch<React.SetStateAction<string>>
  handleArtifactsBlur: () => void
} => {
  const [purpose, setPurpose] = useState(sessionDetail?.purpose || '')
  const [background, setBackground] = useState(sessionDetail?.background || '')
  const [roles, setRoles] = useState(sessionDetail?.roles?.join(', ') || '')
  const [procedure, setProcedure] = useState(sessionDetail?.procedure || '')
  const [artifacts, setArtifacts] = useState(sessionDetail?.artifacts?.join(', ') || '')

  const handlePurposeBlur = useCallback((): void => {
    if (!currentSessionId) return
    onMetaSave(currentSessionId, { purpose: purpose })
  }, [currentSessionId, onMetaSave, purpose])

  const handleBackgroundBlur = useCallback((): void => {
    if (!currentSessionId) return
    onMetaSave(currentSessionId, { background: background })
  }, [currentSessionId, onMetaSave, background])

  const handleRolesBlur = useCallback((): void => {
    if (!currentSessionId) return
    onMetaSave(currentSessionId, {
      roles: roles
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    })
  }, [currentSessionId, onMetaSave, roles])

  const handleProcedureBlur = useCallback((): void => {
    if (!currentSessionId) return
    onMetaSave(currentSessionId, { procedure: procedure })
  }, [currentSessionId, onMetaSave, procedure])

  const handleArtifactsBlur = useCallback((): void => {
    if (!currentSessionId) return
    onMetaSave(currentSessionId, {
      artifacts: artifacts
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    })
  }, [currentSessionId, onMetaSave, artifacts])

  return {
    purpose,
    setPurpose,
    handlePurposeBlur,
    background,
    setBackground,
    handleBackgroundBlur,
    roles,
    setRoles,
    handleRolesBlur,
    procedure,
    setProcedure,
    handleProcedureBlur,
    artifacts,
    setArtifacts,
    handleArtifactsBlur,
  }
}
