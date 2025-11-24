import { useLayoutEffect } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'

export const useSessionMetaBasicLifecycle = (
  sessionDetail: SessionDetail,
  formContext: UseFormReturn | undefined
): void => {
  const setValue = formContext?.setValue

  // Sync sessionDetail changes to form values to avoid visual flicker
  useLayoutEffect(() => {
    if (sessionDetail.roles) {
      setValue?.('roles', sessionDetail.roles)
    }
    if (sessionDetail.procedure) {
      setValue?.('procedure', sessionDetail.procedure)
    }
    if (sessionDetail.artifacts) {
      setValue?.('artifacts', sessionDetail.artifacts)
    }
  }, [sessionDetail, setValue])
}
