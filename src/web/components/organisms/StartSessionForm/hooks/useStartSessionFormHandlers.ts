import { useCallback, useState } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'

import { useStartSessionFormActions } from './useStartSessionFormActions'
import type { StartSessionFormInputs } from '../schema'

export const useStartSessionFormHandlers = (): {
  handleCancel: () => void
  handleCreateClick: () => Promise<void>
  isSubmitting: boolean
} => {
  const { startSessionAction } = useStartSessionFormActions()
  const formContext = useOptionalFormContext<StartSessionFormInputs>()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    async (data: StartSessionFormInputs): Promise<void> => {
      try {
        const result = await startSessionAction(data)
        window.location.href = `/session/${result.session_id}`
      } catch (error: unknown) {
        // Log submitted hyperparameters and entire form values for debugging
        try {
          console.error('StartSession API error:', (error as Error).message)
          // Print the data that was attempted to be submitted
          console.log('StartSession submitted data:', data)
        } catch {
          // ignore logging errors
        }
        throw error
      }
    },
    [startSessionAction]
  )
  const onFormError = useCallback(
    (errors: unknown): void => {
      try {
        console.error('StartSession form validation errors:', errors)
        // If we have access to form context, print current values so we can inspect hyperparameters
        const values = formContext?.getValues ? formContext.getValues() : undefined
        console.log('StartSession current form values (on error):', values)
      } catch {
        // ignore
      }
    },
    [formContext]
  )

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

  return {
    handleCancel,
    handleCreateClick,
    isSubmitting
  }
}
