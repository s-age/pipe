import { useCallback } from 'react'
import type { SubmitHandler } from 'react-hook-form'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { startSession } from '@/lib/api/session/startSession'

import type { StartSessionFormInputs } from '../schema'

type UseStartSessionFormHandlersProperties = {
  handleSubmit: (handler: SubmitHandler<StartSessionFormInputs>) => () => Promise<void>
}

export const useStartSessionFormHandlers = ({
  handleSubmit
}: UseStartSessionFormHandlersProperties): {
  handleCancel: () => void
  handleCreateClick: () => void
  noop: () => Promise<void>

  noopOnSessionUpdate: (_data: SessionDetail | null) => void
} => {
  const toast = useToast()

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
          toast.failure('Failed to create session: No session ID returned.')
        }
      } catch (error_: unknown) {
        toast.failure(
          (error_ as Error).message || 'An error occurred during session creation.'
        )
      }
    },
    [toast]
  )

  const handleCreateClick = useCallback((): void => {
    void handleSubmit(onFormSubmit)()
  }, [handleSubmit, onFormSubmit])

  const noop = useCallback(async () => {}, [])

  const noopOnSessionUpdate = useCallback((_data: SessionDetail | null) => {}, [])

  return {
    handleCancel,
    handleCreateClick,
    noop,
    noopOnSessionUpdate
  }
}
