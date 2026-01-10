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
  saveStatus: 'idle' | 'success' | 'error'
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
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const wrappedSubmit = useCallback(
    async (data: SessionMetaFormInputs) => {
      setIsSubmitting(true)
      setSaveStatus('idle')
      try {
        await onSubmit(data)
        setSaveStatus('success')
      } catch {
        setSaveStatus('error')
      } finally {
        setIsSubmitting(false)
      }
    },
    [onSubmit]
  )

  const handleSaveClick = useCallback(() => {
    if (formContext?.handleSubmit) {
      // Type guard: verify handleSubmit exists and call it
      const submitHandler = formContext.handleSubmit(wrappedSubmit as never)
      if (typeof submitHandler === 'function') {
        // Intentionally not awaiting - errors are handled in Actions layer
        void submitHandler()
      }
    }
  }, [formContext, wrappedSubmit])

  return { onSubmit: wrappedSubmit, isSubmitting, saveStatus, handleSaveClick }
}
