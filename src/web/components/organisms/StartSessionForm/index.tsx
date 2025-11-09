import type { JSX } from 'react'
import type { SubmitHandler } from 'react-hook-form'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { CheckboxField } from '@/components/molecules/CheckboxField'
import { InputField } from '@/components/molecules/InputField'
import { SelectField } from '@/components/molecules/SelectField'
import { TextareaField } from '@/components/molecules/TextareaField'
import type { Settings } from '@/lib/api/settings/getSettings'

import { useStartSessionForm } from './hooks/useStartSessionForm'
import type { StartSessionFormInputs } from './schema'
import {
  formContainer,
  fieldsetContainer,
  legendStyle,
  hyperparametersGrid,
  errorMessageStyle,
} from './style.css'

// Schema imported from ./schema

type StartSessionFormProperties = {
  onSubmit: SubmitHandler<StartSessionFormInputs>
  sessions: { value: string; label: string }[]
  defaultSettings: Settings | null
}

export const StartSessionForm: (
  properties: StartSessionFormProperties,
) => JSX.Element = ({ onSubmit, sessions, defaultSettings }) => {
  const {
    control,
    handleSubmit: formHandleSubmit,
    onFormSubmit,
    errors,
    isSubmitting,
    temperatureValue,
    topPValue,
    topKValue,
    parentSessionOptions,
    handleCancel,
  } = useStartSessionForm({ onSubmit, sessions, defaultSettings })

  return (
    <div className={formContainer}>
      <Heading level={1}>Create New Session</Heading>
      <form onSubmit={formHandleSubmit(onFormSubmit)}>
        <InputField
          control={control}
          name="purpose"
          label="Purpose:"
          id="purpose"
          required={true}
        />
        <TextareaField
          control={control}
          name="background"
          label="Background:"
          id="background"
          required={true}
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
          required={true}
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
        <Button type="button" kind="secondary" size="default" onClick={handleCancel}>
          Cancel
        </Button>
        {Object.keys(errors).length > 0 && (
          <p className={errorMessageStyle}>Please correct the errors in the form.</p>
        )}
      </form>
    </div>
  )
}

// Default export removed — use named export `StartSessionForm`
