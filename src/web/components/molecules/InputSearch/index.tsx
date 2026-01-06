import React from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { IconSearch } from '@/components/atoms/IconSearch'

import { useInputSearchHandlers } from './hooks/useInputSearchHandlers'
import { container, input, button } from './style.css'

type InputSearchProperties = {
  name?: string
  placeholder?: string
  register?: UseFormRegister<FieldValues>
  value?: string
  onChange?: (value: string) => void
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void
  onSubmit?: (value: string) => void
}

export const InputSearch = React.forwardRef<HTMLInputElement, InputSearchProperties>(
  (
    { name, onChange, onKeyDown, onSubmit, placeholder = 'Search...', register, value },
    reference
  ) => {
    const { handleChange, handleSubmit, registerProperties } = useInputSearchHandlers({
      value,
      onChange,
      onSubmit,
      register,
      name
    })

    return (
      <form className={container} onSubmit={handleSubmit} role="search">
        <input
          ref={reference}
          className={input}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onKeyDown={onKeyDown}
          aria-label="Search"
          {...registerProperties}
          name={name}
        />
        <button type="submit" className={button} aria-label="Search">
          <IconSearch size={18} />
        </button>
      </form>
    )
  }
)

InputSearch.displayName = 'InputSearch'

// Default export removed — use named export `InputSearch`
