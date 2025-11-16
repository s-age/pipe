import { useCallback } from 'react'
import type { SubmitHandler } from 'react-hook-form'

import { useStartSessionFormActions } from './useStartSessionFormActions'
import type { StartSessionFormInputs } from '../schema'

type UseStartSessionFormHandlersProperties = {
  handleSubmit: (handler: SubmitHandler<StartSessionFormInputs>) => () => Promise<void>
}

export const useStartSessionFormHandlers = ({
  handleSubmit
}: UseStartSessionFormHandlersProperties): {
  handleCancel: () => void
  handleCreateClick: () => void
} => {
  const { startSessionAction } = useStartSessionFormActions()

  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    async (data: StartSessionFormInputs): Promise<void> => {
      const result = await startSessionAction(data)
      window.location.href = `/session/${result.session_id}`
    },
    [startSessionAction]
  )

  const handleCreateClick = useCallback((): void => {
    void handleSubmit(onFormSubmit)()
  }, [handleSubmit, onFormSubmit])

  return {
    handleCancel,
    handleCreateClick
  }
}
