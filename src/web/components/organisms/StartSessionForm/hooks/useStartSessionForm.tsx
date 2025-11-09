import { zodResolver } from '@hookform/resolvers/zod'
import { useCallback } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import type { SubmitHandler, UseFormReturn } from 'react-hook-form'

import type { StartSessionRequest } from '@/lib/api/session/startSession'
import type { Settings } from '@/lib/api/settings/getSettings'

import type { StartSessionFormInputs } from '../schema'
import { formSchema } from '../schema'

type UseStartSessionFormProperties = {
  onSubmit: SubmitHandler<StartSessionFormInputs>
  sessions: { value: string; label: string }[]
  defaultSettings: Settings | null
}

export const useStartSessionForm = ({
  onSubmit,
  sessions,
  defaultSettings,
}: UseStartSessionFormProperties): {
  control: UseFormReturn<StartSessionFormInputs>['control']
  handleSubmit: UseFormReturn<StartSessionFormInputs>['handleSubmit']
  onFormSubmit: SubmitHandler<StartSessionFormInputs>
  errors: UseFormReturn<StartSessionFormInputs>['formState']['errors']
  isSubmitting: boolean
  temperatureValue: number | null
  topPValue: number | null
  topKValue: number | null
  parentSessionOptions: { value: string; label: string }[]
  handleCancel: () => void
  reset: UseFormReturn<StartSessionFormInputs>['reset']
} => {
  const {
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<StartSessionFormInputs>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      purpose: '',
      background: '',
      roles: null,
      parent: null,
      references: null,
      artifacts: null,
      procedure: null,
      instruction: '',
      multi_step_reasoning_enabled: false,
      hyperparameters: {
        temperature: defaultSettings?.parameters?.temperature ?? 0.7,
        top_p: defaultSettings?.parameters?.top_p ?? 0.9,
        top_k: defaultSettings?.parameters?.top_k ?? 5,
      },
    },
  })

  const temperatureValue = useWatch({ control, name: 'hyperparameters.temperature' })
  const topPValue = useWatch({ control, name: 'hyperparameters.top_p' })
  const topKValue = useWatch({ control, name: 'hyperparameters.top_k' })

  const parentSessionOptions = [{ value: '', label: 'None' }, ...sessions]

  const handleCancel = useCallback(() => {
    window.location.href = '/'
  }, [])

  const onFormSubmit = useCallback(
    (data: StartSessionFormInputs) => onSubmit(data as StartSessionRequest),
    [onSubmit],
  )

  return {
    control,
    handleSubmit,
    onFormSubmit,
    errors,
    isSubmitting,
    temperatureValue,
    topPValue,
    topKValue,
    parentSessionOptions,
    handleCancel,
    reset,
  }
}
