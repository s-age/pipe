import React from 'react'

import { useSessionMetaActions } from '@/components/organisms/SessionMeta/hooks/useSessionMetaActions'
import type { SessionMetaFormInputs } from '@/components/organisms/SessionMeta/schema'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaHandlersProperties = {
  sessionDetail: SessionDetail | null
  onRefresh: () => Promise<void>
}
export const useSessionMetaHandlers = ({
  sessionDetail,
  onRefresh
}: UseSessionMetaHandlersProperties): {
  defaultValues: SessionMetaFormInputs
  onSubmit: (data: SessionMetaFormInputs) => void
  isSubmitting: boolean
  saved: boolean
} => {
  const { handleMetaSave } = useSessionMetaActions({ onRefresh })

  const defaultValues = React.useMemo<SessionMetaFormInputs>(
    () => ({
      purpose: sessionDetail?.purpose ?? null,
      background: sessionDetail?.background ?? null,
      roles: sessionDetail?.roles ?? null,
      procedure: sessionDetail?.procedure ?? null,
      references:
        sessionDetail?.references?.map((reference) => ({
          path: reference.path,
          ttl: reference.ttl ?? 3,
          persist: reference.persist ?? false,
          disabled: reference.disabled ?? false
        })) ?? [],
      artifacts: sessionDetail?.artifacts ?? null,
      hyperparameters: sessionDetail?.hyperparameters ?? null,
      multi_step_reasoning: sessionDetail?.multi_step_reasoning_enabled ?? false
    }),
    [sessionDetail]
  )

  const onSubmit = React.useCallback(
    (data: SessionMetaFormInputs) => {
      if (!sessionDetail?.session_id) return

      // roles, artifacts, references, procedure はすべて既に正しい形式なので変換不要
      void handleMetaSave(sessionDetail?.session_id, data as EditSessionMetaRequest)
    },
    [sessionDetail?.session_id, handleMetaSave]
  )

  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [saved, setSaved] = React.useState(false)

  const wrappedSubmit = React.useCallback(
    async (data: SessionMetaFormInputs) => {
      setIsSubmitting(true)
      void onSubmit(data)
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2000)
      setIsSubmitting(false)
    },
    [onSubmit]
  )

  return { defaultValues, onSubmit: wrappedSubmit, isSubmitting, saved }
}
