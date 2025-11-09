import type { JSX } from 'react'

import { IconSearch } from '@/components/atoms/IconSearch'

import { useInputSearch } from './hooks/useInputSearch'
import { container, input, button } from './style.css'

type InputSearchProperties = {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSubmit?: (value: string) => void
}

export const InputSearch = ({
  placeholder = 'Search...',
  value,
  onChange,
  onSubmit,
}: InputSearchProperties): JSX.Element => {
  const { handleSubmit, handleChange } = useInputSearch({ value, onChange, onSubmit })

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

// Default export removed — use named export `InputSearch`
