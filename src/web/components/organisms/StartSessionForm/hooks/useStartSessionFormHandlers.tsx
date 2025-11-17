import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'

import { useStartSessionFormActions } from './useStartSessionFormActions'
import type { StartSessionFormInputs } from '../schema'

export const useStartSessionFormHandlers = (): {
  handleCancel: () => void
  handleCreateClick: () => void
} => {
  const { startSessionAction } = useStartSessionFormActions()
  const formContext = useOptionalFormContext<StartSessionFormInputs>()

  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    async (data: StartSessionFormInputs): Promise<void> => {
      // Submit handler — no debug logging
      const result = await startSessionAction(data)
      window.location.href = `/session/${result.session_id}`
    },
    [startSessionAction]
  )

  const handleCreateClick = useCallback((): void => {
    void formContext?.handleSubmit(onFormSubmit)()
  }, [formContext, onFormSubmit])

  return {
    handleCancel,
    handleCreateClick
  }
}
