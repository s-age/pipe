import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'

import { useSelect } from './hooks/useSelect'
import type { SelectOption } from './hooks/useSelect'
import { useSelectHandlers } from './hooks/useSelectHandlers'
import { useSelectUI } from './hooks/useSelectLifecycle'
import {
  selectStyle,
  trigger,
  panel,
  option,
  optionHighlighted,
  searchInput
} from './style.css'

type SelectProperties = {
  register?: UseFormRegister<Record<string, unknown>>
  name?: string
  options?: Array<string | SelectOption>
  searchable?: boolean
  placeholder?: string
} & SelectHTMLAttributes<HTMLSelectElement>

export const Select = (properties: SelectProperties): JSX.Element => {
  const {
    register,
    name,
    options,
    searchable = false,
    placeholder,
    className,
    ...rest
  } = properties

  const {
    registerProperties,
    normalizedOptions,
    filteredOptions,
    selectedValue,
    isOpen,
    setIsOpen,
    query,
    setQuery,
    listReference,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValue
  } = useSelect({
    register,
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string | undefined,
    searchable
  })

  const {
    toggleOpen,
    handleKeyDownReact,
    handleSearchChange,
    handleOptionClickReact,
    handleMouseEnterReact,
    handleMouseLeaveReact
  } = useSelectHandlers({
    isOpen,
    setIsOpen,
    filteredOptions,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValue,
    setQuery
  })

  const { rootReference } = useSelectUI({
    isOpen,
    close: () => setIsOpen(false),
    clearHighlight: () => setHighlightedIndex(-1)
  })

  // If no options specified and not searchable, fall back to native select for full compatibility
  if (!options && !searchable) {
    return <select className={selectStyle} {...rest} />
  }

  // Use normalizedOptions to resolve the label for the currently selected option id
  // and treat empty-string ('') as a valid original value.
  const selectedOption =
    typeof selectedValue !== 'undefined'
      ? normalizedOptions.find((o) => o.id === selectedValue)
      : undefined
  const selectedLabel = selectedOption?.label ?? placeholder ?? ''

  return (
    <div ref={rootReference} className={`${className ?? selectStyle}`}>
      {/* Hidden native select kept for form integrations (RHF / native form submit) */}
      <select
        {...rest}
        {...registerProperties}
        name={name}
        // expose the ORIGINAL value to the native/registered select
        value={selectedOption?.value ?? rest.value}
        hidden={true}
      >
        {(normalizedOptions ?? []).map((opt) => (
          <option key={opt.id ?? opt.value} value={opt.value}>
            {typeof opt.label === 'string' ? opt.label : String(opt.value)}
          </option>
        ))}
      </select>

      <div
        tabIndex={0}
        role="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={toggleOpen}
        onKeyDown={handleKeyDownReact}
        className={trigger}
      >
        <span>{selectedLabel}</span>
      </div>
      {isOpen && (
        <div>
          {searchable && (
            <input
              type="text"
              value={query}
              onChange={handleSearchChange}
              aria-label="Search options"
              className={searchInput}
            />
          )}

          <ul
            ref={listReference}
            role="listbox"
            aria-hidden={!isOpen}
            className={panel}
          >
            {filteredOptions.map((opt, index) => (
              <li
                key={opt.id ?? opt.value}
                role="option"
                onClick={handleOptionClickReact}
                onMouseEnter={handleMouseEnterReact}
                onMouseLeave={handleMouseLeaveReact}
                className={
                  highlightedIndex === index ? `${option} ${optionHighlighted}` : option
                }
                data-value={opt.id ?? opt.value}
                data-index={String(index)}
              >
                {opt.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// (Removed temporary default export) Use named export `Select`.
