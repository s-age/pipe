import { useCallback, useState } from 'react'

import type { FormMethods } from '@/components/organisms/Form'
import { useSessionMetaActions } from '@/components/organisms/SessionMeta/hooks/useSessionMetaActions'
import type { SessionMetaFormInputs } from '@/components/organisms/SessionMeta/schema'
import type { EditSessionMetaRequest } from '@/lib/api/meta/editSessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

type UseSessionMetaHandlersProperties = {
  sessionDetail: SessionDetail
  formContext?: FormMethods
  onRefresh: () => Promise<void>
}
export const useSessionMetaHandlers = ({
  sessionDetail,
  formContext,
  onRefresh
}: UseSessionMetaHandlersProperties): {
  isSubmitting: boolean
  handleSaveClick: () => void
  onSubmit: (data: SessionMetaFormInputs) => Promise<void>
} => {
  const { handleMetaSave } = useSessionMetaActions()

  const onSubmit = useCallback(
    async (data: SessionMetaFormInputs) => {
      if (!sessionDetail.sessionId) return

      // Note: SessionMetaFormInputs and EditSessionMetaRequest have compatible shapes
      // roles, artifacts, procedure, hyperparameters are already in the correct format
      await handleMetaSave(
        sessionDetail.sessionId,
        data as unknown as EditSessionMetaRequest
      )
      await onRefresh()
    },
    [sessionDetail.sessionId, handleMetaSave, onRefresh]
  )

  const [isSubmitting, setIsSubmitting] = useState(false)

  const wrappedSubmit = useCallback(
    async (data: SessionMetaFormInputs) => {
      setIsSubmitting(true)
      await onSubmit(data)
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
