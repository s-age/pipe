import { clsx } from 'clsx'
import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'

import { Box } from '@/components/molecules/Box'

import { useSelect } from './hooks/useSelect'
import type { SelectOption } from './hooks/useSelect'
import { useSelectHandlers } from './hooks/useSelectHandlers'
import { useSelectLifecycle } from './hooks/useSelectLifecycle'
import {
  selectStyle,
  trigger,
  panel,
  option,
  optionHighlighted,
  optionDisabled,
  searchInput
} from './style.css'

type SelectProperties = {
  name?: string
  options?: Array<string | SelectOption>
  placeholder?: string
  register?: UseFormRegister<Record<string, unknown>>
  searchable?: boolean
} & SelectHTMLAttributes<HTMLSelectElement>

export const Select = (properties: SelectProperties): JSX.Element => {
  const {
    className,
    name,
    options,
    placeholder,
    register,
    searchable = false,
    ...rest
  } = properties

  const {
    filteredOptions,
    highlightedIndex,
    isOpen,
    listReference,
    normalizedOptions,
    query,
    registerProperties,
    selectedLabel,
    selectedNativeValue,
    setHighlightedIndex,
    setIsOpen,
    setQuery,
    setSelectedValue
  } = useSelect({
    register,
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string | undefined,
    searchable,
    placeholder
  })

  const {
    handleKeyDown,
    handleMouseEnter,
    handleMouseLeave,
    handleOptionClick,
    handleSearchChange,
    toggleOpen
  } = useSelectHandlers({
    isOpen,
    setIsOpen,
    filteredOptions,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValue,
    setQuery,
    onChange: rest.onChange
  })

  const { rootReference } = useSelectLifecycle({
    isOpen,
    close: () => setIsOpen(false),
    clearHighlight: () => setHighlightedIndex(-1)
  })

  // If no options specified and not searchable, fall back to native select for full compatibility
  if (!options && !searchable) {
    return <select className={selectStyle} {...rest} />
  }

  // Presentational: use label/native value computed by the hook
  const displayLabel = selectedLabel ?? placeholder ?? ''

  return (
    <Box ref={rootReference} className={clsx(selectStyle, className)}>
      {/* Hidden native select kept for form integrations (RHF / native form submit) */}
      <select
        {...rest}
        {...registerProperties}
        name={name}
        // expose the ORIGINAL value to the native/registered select
        value={selectedNativeValue ?? rest.value}
        hidden={true}
      >
        {(normalizedOptions ?? []).map((opt) => (
          <option key={opt.id ?? opt.value} value={opt.value} disabled={opt.disabled}>
            {typeof opt.label === 'string' ? opt.label : String(opt.value)}
          </option>
        ))}
      </select>

      <Box
        tabIndex={0}
        role="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={toggleOpen}
        onKeyDown={handleKeyDown}
        className={trigger}
      >
        <Box as="span">{displayLabel}</Box>
      </Box>
      {isOpen && (
        <Box>
          {searchable && (
            <input
              type="text"
              value={query}
              onChange={handleSearchChange}
              aria-label="Search options"
              className={searchInput}
            />
          )}

          <Box
            as="ul"
            ref={listReference}
            role="listbox"
            aria-hidden={!isOpen}
            className={panel}
          >
            {filteredOptions.map((opt, index) => (
              <Box
                as="li"
                key={opt.id ?? opt.value}
                role="option"
                onClick={opt.disabled ? undefined : handleOptionClick}
                onMouseEnter={opt.disabled ? undefined : handleMouseEnter}
                onMouseLeave={opt.disabled ? undefined : handleMouseLeave}
                className={clsx(
                  option,
                  highlightedIndex === index && optionHighlighted,
                  opt.disabled && optionDisabled
                )}
                data-value={opt.id ?? opt.value}
                data-index={String(index)}
                aria-disabled={opt.disabled}
              >
                {opt.label}
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  )
}

// (Removed temporary default export) Use named export `Select`.
