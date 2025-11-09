import { useCallback } from 'react'
import type { FormEvent, ChangeEvent } from 'react'

type Properties = {
  value?: string
  onChange?: (value: string) => void
  onSubmit?: (value: string) => void
}

export function useInputSearch({ value, onChange, onSubmit }: Properties): {
  handleSubmit: (event: FormEvent) => void
  handleChange: (event: ChangeEvent<HTMLInputElement>) => void
} {
  const handleSubmit = useCallback(
    (event: FormEvent): void => {
      event.preventDefault()
      if (onSubmit) onSubmit((value ?? '') as string)
    },
    [onSubmit, value],
  )

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>): void => {
      if (onChange) onChange(event.target.value)
    },
    [onChange],
  )

  return { handleSubmit, handleChange }
}
