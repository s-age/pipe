import { useCallback, type JSX, type ChangeEvent } from 'react'
import type { FormEvent } from 'react'

import IconSearch from '@/components/atoms/IconSearch'

import { container, input, button } from './style.css'

type InputSearchProperties = {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSubmit?: (value: string) => void
}

const InputSearch = ({
  placeholder = 'Search...',
  value,
  onChange,
  onSubmit,
}: InputSearchProperties): JSX.Element => {
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

  return (
    <form className={container} onSubmit={handleSubmit} role="search">
      <input
        className={input}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        aria-label="Search"
      />
      <button type="submit" className={button} aria-label="Search">
        <IconSearch size={18} />
      </button>
    </form>
  )
}

export default InputSearch
