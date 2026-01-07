import { useEffect } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'

type UseArtifactListLifecycleProperties = {
  currentArtifacts: string[]
  sessionDetail: SessionDetail
  formContext?: UseFormReturn
}

export const useArtifactListLifecycle = ({
  currentArtifacts,
  sessionDetail,
  formContext
}: UseArtifactListLifecycleProperties): void => {
  // Sync form with updated sessionDetail.artifacts from server
  useEffect(() => {
    if (sessionDetail.sessionId && formContext && sessionDetail.artifacts) {
      // Only update if sessionDetail.artifacts differs from form value
      if (
        JSON.stringify(sessionDetail.artifacts) !== JSON.stringify(currentArtifacts)
      ) {
        formContext.setValue('artifacts', sessionDetail.artifacts)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionDetail.artifacts, sessionDetail.sessionId])
}
