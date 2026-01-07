import type { TextareaHTMLAttributes, JSX } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import { useTextArea } from './hooks/useTextArea'
import { textareaStyle } from './style.css'

type TextAreaProperties = Omit<
  TextareaHTMLAttributes<HTMLTextAreaElement>,
  'onChange'
> & {
  name?: string
  register?: UseFormRegister<FieldValues>
  onChange?: (value: string) => void
  /**
   * Accessible label for the textarea.
   * Use when the textarea does not have a visible label element.
   */
  'aria-label'?: string
  /**
   * ID(s) of element(s) that describe this textarea.
   * Use to link error messages, hints, or help text.
   */
  'aria-describedby'?: string
  /**
   * Indicates whether the textarea is required.
   * Usually the native `required` attribute is sufficient.
   */
  'aria-required'?: boolean
  /**
   * Indicates the textarea has a validation error.
   * Set to true when displaying error messages.
   */
  'aria-invalid'?: boolean
}

export const TextArea: (properties: TextAreaProperties) => JSX.Element = (
  properties
) => {
  const {
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedby,
    'aria-required': ariaRequired,
    'aria-invalid': ariaInvalid,
    name,
    onChange: _onChange,
    register: _register,
    ...restProperties
  } = properties
  // reference the binding to satisfy lint rules (we intentionally don't spread it)
  void _register
  // intentionally reference `_onChange` so linters know it's excluded from
  // `restProps` which will be spread onto the native textarea. The component's
  // onChange has a different signature (value:string) and we bridge it via the hook.
  void _onChange

  const { handleChange, id, registerProperties, visibleValue } = useTextArea(
    properties as unknown as Parameters<typeof useTextArea>[0]
  )

  const rp = registerProperties as UseFormRegisterReturn | undefined

  return (
    <textarea
      id={id}
      className={textareaStyle}
      {...restProperties}
      {...(visibleValue !== undefined ? { value: visibleValue } : {})}
      name={name}
      {...(rp ? (rp as unknown as Record<string, unknown>) : {})}
      onChange={handleChange}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      aria-required={ariaRequired}
      aria-invalid={ariaInvalid}
    />
  )
}

// (Removed temporary default export) Use named export `TextArea`.
