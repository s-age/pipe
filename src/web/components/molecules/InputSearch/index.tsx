import React from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { IconSearch } from '@/components/atoms/IconSearch'

import { useInputSearch } from './hooks/useInputSearchHandlers'
import { container, input, button } from './style.css'

type InputSearchProperties = {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSubmit?: (value: string) => void
  register?: UseFormRegister<FieldValues>
  name?: string
  onKeyDown?: (event: React.KeyboardEvent<HTMLInputElement>) => void
}

export const InputSearch = React.forwardRef<HTMLInputElement, InputSearchProperties>(
  (
    { placeholder = 'Search...', value, onChange, onSubmit, register, name, onKeyDown },
    reference
  ) => {
    const { handleSubmit, handleChange, registerProperties } = useInputSearch({
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
