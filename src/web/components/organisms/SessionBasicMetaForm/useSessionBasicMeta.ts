import { useState, useCallback } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionBasicMetaProperties = {
  sessionDetail: SessionDetail | null
}

export const useSessionBasicMeta = ({
  sessionDetail,
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
    // 自動保存は行わない
  }, [])

  const handleBackgroundBlur = useCallback((): void => {
    // 自動保存は行わない
  }, [])

  const handleRolesBlur = useCallback((): void => {
    // 自動保存は行わない
  }, [])

  const handleProcedureBlur = useCallback((): void => {
    // 自動保存は行わない
  }, [])

  const handleArtifactsBlur = useCallback((): void => {
    // 自動保存は行わない
  }, [])

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
