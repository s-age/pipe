import { useCallback } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useArtifactListActions } from './useArtifactListActions'

type UseArtifactListHandlersProperties = {
  sessionDetail: SessionDetail
  formContext?: UseFormReturn
  refreshSessions: () => Promise<void>
}

type UseArtifactListHandlersReturn = {
  handleArtifactsChange: (artifactPaths: string[]) => Promise<void>
}

export const useArtifactListHandlers = ({
  sessionDetail,
  formContext,
  refreshSessions
}: UseArtifactListHandlersProperties): UseArtifactListHandlersReturn => {
  const { updateArtifacts } = useArtifactListActions()

  const handleArtifactsChange = useCallback(
    async (artifactPaths: string[]): Promise<void> => {
      // Update form state immediately for optimistic UI
      formContext?.setValue('artifacts', artifactPaths)

      if (!sessionDetail.sessionId) {
        // New session: form state update only
        return
      }

      // Existing session: update via API
      await updateArtifacts(sessionDetail.sessionId, artifactPaths)
      await refreshSessions()
    },
    [sessionDetail.sessionId, formContext, updateArtifacts, refreshSessions]
  )

  return {
    handleArtifactsChange
  }
}
