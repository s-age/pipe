import { useCallback } from 'react'
import type { SubmitHandler } from 'react-hook-form'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { startSession } from '@/lib/api/session/startSession'
import { emitToast } from '@/lib/toastEvents'

import type { StartSessionFormInputs } from '../schema'

type UseStartSessionFormHandlersProperties = {
  handleSubmit: (handler: SubmitHandler<StartSessionFormInputs>) => () => Promise<void>
}

export const useStartSessionFormHandlers = ({
  handleSubmit
}: UseStartSessionFormHandlersProperties): {
  handleCancel: () => void
  handleCreateClick: () => void
  noopOnSessionUpdate: (_data: SessionDetail | null) => void
} => {
  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    async (data: StartSessionFormInputs): Promise<void> => {
      try {
        const result = await startSession(data)
        if (result.session_id) {
          window.location.href = `/session/${result.session_id}`
        } else {
          emitToast.failure('Failed to create session: No session ID returned.')
        }
      } catch (error_: unknown) {
        emitToast.failure(
          (error_ as Error).message || 'An error occurred during session creation.'
        )
      }
    },
    []
  )

  const handleCreateClick = useCallback((): void => {
    void handleSubmit(onFormSubmit)()
  }, [handleSubmit, onFormSubmit])

  const noopOnSessionUpdate = useCallback((_data: SessionDetail | null) => {}, [])

  return {
    handleCancel,
    handleCreateClick,
    noopOnSessionUpdate
  }
}
