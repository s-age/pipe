import React from 'react'

import { useSessionMetaSaver } from '@/components/organisms/SessionMeta/useSessionMetaSaver'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Actions } from '@/stores/useChatHistoryStore'

type UseSessionMetaFormProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  actions: Actions
}
export const useSessionMetaForm = ({
  sessionDetail,
  currentSessionId,
  actions
}: UseSessionMetaFormProperties): {
  defaultValues: Record<string, unknown>
  onSubmit: (data: EditSessionMetaRequest) => void
  isSubmitting: boolean
  saved: boolean
} => {
  const { handleMetaSave } = useSessionMetaSaver({ actions })

  const defaultValues = React.useMemo(
    () => ({
      purpose: sessionDetail?.purpose ?? '',
      background: sessionDetail?.background ?? '',
      roles: sessionDetail?.roles?.join(', ') ?? '',
      procedure: sessionDetail?.procedure ?? '',
      artifacts: sessionDetail?.artifacts?.join(', ') ?? ''
    }),
    [sessionDetail]
  )

  const onSubmit = React.useCallback(
    (data: EditSessionMetaRequest) => {
      if (!currentSessionId) return

      const mutable: Record<string, unknown> = { ...data }

      if (typeof mutable.roles === 'string') {
        mutable.roles = mutable.roles
          .split(',')
          .map((s: string) => s.trim())
          .filter(Boolean)
      }

      if (typeof mutable.artifacts === 'string') {
        mutable.artifacts = mutable.artifacts
          .split(',')
          .map((s: string) => s.trim())
          .filter(Boolean)
      }

      void handleMetaSave(currentSessionId, mutable as EditSessionMetaRequest)
    },
    [currentSessionId, handleMetaSave]
  )

  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [saved, setSaved] = React.useState(false)

  const wrappedSubmit = React.useCallback(
    async (data: Record<string, unknown>) => {
      setIsSubmitting(true)
      try {
        await onSubmit(data)
        setSaved(true)
        window.setTimeout(() => setSaved(false), 2000)
      } finally {
        setIsSubmitting(false)
      }
    },
    [onSubmit]
  )

  return { defaultValues, onSubmit: wrappedSubmit, isSubmitting, saved }
}
