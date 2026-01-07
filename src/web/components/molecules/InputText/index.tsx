import type { InputHTMLAttributes, JSX } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

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

export const InputText = ({
  name,
  register,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedby,
  'aria-required': ariaRequired,
  'aria-invalid': ariaInvalid,
  ...rest
}: InputTextProperties): JSX.Element => {
  const { registerProperties } = useInputText({ register, name })

  const rp = registerProperties as UseFormRegisterReturn | undefined

  return (
    <input
      type="text"
      className={inputStyle}
      {...rest}
      name={name}
      {...(rp ? (rp as unknown as Record<string, unknown>) : {})}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      aria-required={ariaRequired}
      aria-invalid={ariaInvalid}
    />
  )
}

// Default export removed — use named export `InputText`
