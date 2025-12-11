import { useMemo } from 'react'

import type { SessionMetaFormInputs } from '@/components/organisms/SessionMeta/schema'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaLifecycleProperties = {
  sessionDetail: SessionDetail
}

export const useSessionMetaLifecycle = ({
  sessionDetail
}: UseSessionMetaLifecycleProperties): {
  computedDefaultValues: SessionMetaFormInputs
} => {
  const computedDefaultValues = useMemo<SessionMetaFormInputs>(
    () => ({
      purpose: sessionDetail.purpose ?? null,
      background: sessionDetail.background ?? null,
      roles: sessionDetail.roles ?? null,
      procedure: sessionDetail.procedure ?? null,
      artifacts: sessionDetail.artifacts ?? null,
      hyperparameters: sessionDetail.hyperparameters ?? null
    }),
    [
      sessionDetail.purpose,
      sessionDetail.background,
      sessionDetail.roles,
      sessionDetail.procedure,
      sessionDetail.artifacts,
      sessionDetail.hyperparameters
    ]
  )

  return { computedDefaultValues }
}
