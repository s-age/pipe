import { useCallback, useState } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import { addToast } from '@/stores/useToastStore'

import { useStartSessionFormActions } from './useStartSessionFormActions'
import type { StartSessionFormInputs } from '../schema'

export const useStartSessionFormHandlers = (): {
  isSubmitting: boolean
  dummyHandler: () => Promise<void>
  handleCancel: () => void
  handleCreateClick: () => Promise<void>
} => {
  const { startSessionAction } = useStartSessionFormActions()
  const formContext = useOptionalFormContext<StartSessionFormInputs>()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    async (data: StartSessionFormInputs): Promise<void> => {
      const result = await startSessionAction(data)
      if (result?.sessionId) {
        window.location.href = `/session/${result.sessionId}`
      }
    },
    [startSessionAction]
  )
  const onFormError = useCallback((_errors: unknown): void => {
    addToast({
      status: 'failure',
      title: 'Form validation failed',
      description: 'Please check all required fields'
    })
  }, [])

  const handleCreateClick = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    try {
      // Pass an onError handler to handleSubmit so validation errors are logged
      await formContext?.handleSubmit(onFormSubmit, onFormError)()
    } finally {
      // If navigation occurs in onFormSubmit (window.location.href) this may
      // not run, but it still ensures the UI shows submitting state while
      // the request is in progress in most cases.
      setIsSubmitting(false)
    }
  }, [formContext, onFormSubmit, onFormError])

  const dummyHandler = useCallback(async (): Promise<void> => {
    // no-op
  }, [])

  return {
    handleCancel,
    handleCreateClick,
    dummyHandler,
    isSubmitting
  }
}
