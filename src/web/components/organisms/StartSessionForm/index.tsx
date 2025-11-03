import { zodResolver } from '@hookform/resolvers/zod'
import { JSX } from 'react'
import { useForm, useWatch, SubmitHandler } from 'react-hook-form'
import * as z from 'zod'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import CheckboxField from '@/components/molecules/CheckboxField'
import InputField from '@/components/molecules/InputField'
import SelectField from '@/components/molecules/SelectField'
import TextareaField from '@/components/molecules/TextareaField'
import { StartSessionRequest } from '@/lib/api/session/startSession'
import { Settings } from '@/lib/api/settings/getSettings'

import {
  formContainer,
  fieldsetContainer,
  legendStyle,
  hyperparametersGrid,
  errorMessageStyle,
} from './style.css'

const formSchema = z.object({
  purpose: z.string().min(1, 'Purpose is required'),
  background: z.string().min(1, 'Background is required'),
  roles: z
    .string()
    .transform((val) =>
      val
        ? val
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null,
    )
    .nullable()
    .default(null),
  parent: z
    .string()
    .transform((val) => (val === '' ? null : val))
    .nullable()
    .default(null),
  references: z
    .string()
    .transform((val) =>
      val
        ? val
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
            .map((path) => ({ path }))
        : null,
    )
    .nullable()
    .default(null),
  artifacts: z
    .string()
    .transform((val) =>
      val
        ? val
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null,
    )
    .nullable()
    .default(null),
  procedure: z
    .string()
    .transform((val) => (val === '' ? null : val))
    .nullable()
    .default(null),
  instruction: z.string().min(1, 'First Instruction is required'),
  multi_step_reasoning_enabled: z.boolean().default(false),
  hyperparameters: z
    .object({
      temperature: z.coerce.number().min(0).max(2).nullable().default(0.7),
      top_p: z.coerce.number().min(0).max(1).nullable().default(0.9),
      top_k: z.coerce.number().min(1).max(50).nullable().default(5),
    })
    .nullable()
    .default(null),
})

type StartSessionFormInputs = z.infer<typeof formSchema>

type StartSessionFormProps = {
  onSubmit: SubmitHandler<StartSessionFormInputs>
  sessions: { value: string; label: string }[]
  defaultSettings: Settings | null
}

const StartSessionForm: (props: StartSessionFormProps) => JSX.Element = ({
  onSubmit,
  sessions,
  defaultSettings,
}) => {
  const {
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
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

  return (
    <div className={formContainer}>
      <Heading level={1}>Create New Session</Heading>
      <form onSubmit={handleSubmit((data) => onSubmit(data as StartSessionRequest))}>
        <InputField
          control={control}
          name="purpose"
          label="Purpose:"
          id="purpose"
          required
        />
        <TextareaField
          control={control}
          name="background"
          label="Background:"
          id="background"
          required
        />
        <InputField
          control={control}
          name="roles"
          label="Roles (comma-separated paths, e.g., roles/engineer.md):"
          id="roles"
        />
        <SelectField
          control={control}
          name="parent"
          label="Parent Session (optional):"
          id="parent"
          options={parentSessionOptions}
        />
        <InputField
          control={control}
          name="references"
          label="References (comma-separated paths):"
          id="references"
        />
        <InputField
          control={control}
          name="artifacts"
          label="Artifacts (comma-separated paths):"
          id="artifacts"
        />
        <InputField
          control={control}
          name="procedure"
          label="Procedure (path to file):"
          id="procedure"
        />
        <TextareaField
          control={control}
          name="instruction"
          label="First Instruction:"
          id="instruction"
          required
        />
        <CheckboxField
          control={control}
          name="multi_step_reasoning_enabled"
          label="Enable Multi-step Reasoning"
          id="multi-step-reasoning"
        />

        <fieldset className={fieldsetContainer}>
          <legend className={legendStyle}>Hyperparameters</legend>
          <div className={hyperparametersGrid}>
            <InputField
              control={control}
              name="hyperparameters.temperature"
              label={`Temperature: ${temperatureValue}`}
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
            />
            <InputField
              control={control}
              name="hyperparameters.top_p"
              label={`Top P: ${topPValue}`}
              id="top_p"
              type="range"
              min="0"
              max="1"
              step="0.1"
            />
            <InputField
              control={control}
              name="hyperparameters.top_k"
              label={`Top K: ${topKValue}`}
              id="top_k"
              type="range"
              min="1"
              max="50"
              step="1"
            />
          </div>
        </fieldset>

        <Button type="submit" kind="primary" size="default" disabled={isSubmitting}>
          {isSubmitting ? 'Creating...' : 'Create Session'}
        </Button>
        <Button
          type="button"
          kind="secondary"
          size="default"
          onClick={() => (window.location.href = '/')}
        >
          Cancel
        </Button>
        {Object.keys(errors).length > 0 && (
          <p className={errorMessageStyle}>Please correct the errors in the form.</p>
        )}
      </form>
    </div>
  )
}

export default StartSessionForm
