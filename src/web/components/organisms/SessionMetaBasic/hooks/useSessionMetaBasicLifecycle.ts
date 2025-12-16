import { useLayoutEffect } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'

export const useSessionMetaBasicLifecycle = (
  sessionDetail: SessionDetail,
  formContext: UseFormReturn | undefined,
  isSubmitting?: boolean
): void => {
  const setValue = formContext?.setValue

  // Sync sessionDetail changes to form values to avoid visual flicker
  useLayoutEffect(() => {
    if (isSubmitting) return // Skip sync during submission to prevent flicker

    if (sessionDetail && sessionDetail.roles) {
      setValue?.('roles', sessionDetail.roles)
    }
    if (sessionDetail && sessionDetail.procedure) {
      setValue?.('procedure', sessionDetail.procedure)
    }
    if (sessionDetail && sessionDetail.artifacts) {
      setValue?.('artifacts', sessionDetail.artifacts)
    }
    if (sessionDetail && sessionDetail.references) {
      setValue?.('references', sessionDetail.references)
    }
  }, [sessionDetail, setValue, isSubmitting])
}
