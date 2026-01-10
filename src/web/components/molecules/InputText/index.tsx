import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useInputText } from './hooks/useInputText'
import { inputStyle } from './style.css'

type InputTextProperties = {
  name?: string
  register?: UseFormRegister<FieldValues>
  /**
   * Accessible label for the input.
   * Use when the input does not have a visible label element.
   */
  'aria-label'?: string
  /**
   * ID(s) of element(s) that describe this input.
   * Use to link error messages, hints, or help text.
   */
  'aria-describedby'?: string
  /**
   * Indicates whether the input is required.
   * Usually the native `required` attribute is sufficient.
   */
  'aria-required'?: boolean
  /**
   * Indicates the input has a validation error.
   * Set to true when displaying error messages.
   */
  'aria-invalid'?: boolean
} & InputHTMLAttributes<HTMLInputElement>

export const InputText = (properties: InputTextProperties): JSX.Element => {
  const {
    'aria-describedby': ariaDescribedby,
    'aria-invalid': ariaInvalid,
    'aria-label': ariaLabel,
    'aria-required': ariaRequired,
    name,
    register,
    ...rest
  } = properties
  // Explicitly exclude register from being spread to the DOM
  void register

  const { registerProperties } = useInputText({ register, name })

  return (
    <input
      type="text"
      className={inputStyle}
      {...rest}
      name={name}
      {...registerProperties}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      aria-required={ariaRequired}
      aria-invalid={ariaInvalid}
    />
  )
}

// Default export removed — use named export `InputText`
