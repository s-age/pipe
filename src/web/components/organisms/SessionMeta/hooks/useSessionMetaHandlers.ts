import { useCallback, useState } from 'react'

import type { FormMethods } from '@/components/organisms/Form'
import { useSessionMetaActions } from '@/components/organisms/SessionMeta/hooks/useSessionMetaActions'
import type { SessionMetaFormInputs } from '@/components/organisms/SessionMeta/schema'
import type { EditSessionMetaRequest } from '@/lib/api/meta/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaHandlersProperties = {
  sessionDetail: SessionDetail
  onRefresh: () => Promise<void>
  formContext?: FormMethods
}
export const useSessionMetaHandlers = ({
  sessionDetail,
  onRefresh,
  formContext
}: UseSessionMetaHandlersProperties): {
  onSubmit: (data: SessionMetaFormInputs) => void
  isSubmitting: boolean
  handleSaveClick: () => void
} => {
  const { handleMetaSave } = useSessionMetaActions({ onRefresh })

  const onSubmit = useCallback(
    (data: SessionMetaFormInputs) => {
      if (!sessionDetail.sessionId) return

      // Note: SessionMetaFormInputs and EditSessionMetaRequest have compatible shapes
      // roles, artifacts, procedure, hyperparameters are already in the correct format
      // Intentionally not awaiting - errors are handled in Actions layer
      void handleMetaSave(
        sessionDetail.sessionId,
        data as unknown as EditSessionMetaRequest
      )
    },
    [sessionDetail.sessionId, handleMetaSave]
  )

  const [isSubmitting, setIsSubmitting] = useState(false)

  const wrappedSubmit = useCallback(
    async (data: SessionMetaFormInputs) => {
      setIsSubmitting(true)
      // Intentionally not awaiting - errors are handled in Actions layer
      void onSubmit(data)
      setIsSubmitting(false)
    },
    [onSubmit]
  )

  const handleSaveClick = useCallback(() => {
    if (formContext?.handleSubmit) {
      // Type guard: verify handleSubmit exists and call it
      const submitHandler = formContext.handleSubmit(onSubmit as never)
      if (typeof submitHandler === 'function') {
        // Intentionally not awaiting - errors are handled in Actions layer
        void submitHandler()
      }
    }
  }, [formContext, onSubmit])

  return { onSubmit: wrappedSubmit, isSubmitting, handleSaveClick }
}
