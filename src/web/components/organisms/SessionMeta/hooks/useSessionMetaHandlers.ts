import { useCallback, useState } from 'react'

import type { FormMethods } from '@/components/organisms/Form'
import { useSessionMetaActions } from '@/components/organisms/SessionMeta/hooks/useSessionMetaActions'
import type { SessionMetaFormInputs } from '@/components/organisms/SessionMeta/schema'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
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
      if (!sessionDetail.session_id) return

      // roles, artifacts, references, procedure はすべて既に正しい形式なので変換不要
      void handleMetaSave(sessionDetail.session_id, data as EditSessionMetaRequest)
    },
    [sessionDetail.session_id, handleMetaSave]
  )

  const [isSubmitting, setIsSubmitting] = useState(false)

  const wrappedSubmit = useCallback(
    async (data: SessionMetaFormInputs) => {
      setIsSubmitting(true)
      void onSubmit(data)
      setIsSubmitting(false)
    },
    [onSubmit]
  )

  const handleSaveClick = useCallback(() => {
    void formContext?.handleSubmit(onSubmit as never)()
  }, [formContext, onSubmit])

  return { onSubmit: wrappedSubmit, isSubmitting, handleSaveClick }
}
