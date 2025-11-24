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
      references:
        sessionDetail.references?.map((reference) => ({
          path: reference.path,
          ttl: reference.ttl ?? 3,
          persist: reference.persist ?? false,
          disabled: reference.disabled ?? false
        })) ?? [],
      artifacts: sessionDetail.artifacts ?? null,
      hyperparameters: sessionDetail.hyperparameters ?? null,
      multi_step_reasoning: sessionDetail.multi_step_reasoning_enabled ?? false
    }),
    [sessionDetail]
  )

  return { computedDefaultValues }
}
