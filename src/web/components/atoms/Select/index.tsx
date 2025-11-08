import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'

import type { SelectOption } from './hooks/useSelect'
import useSelect from './hooks/useSelect'
import useSelectUI from './hooks/useSelectUI'
import {
  selectStyle,
  trigger,
  panel,
  option,
  optionHighlighted,
  searchInput,
} from './style.css'

type SelectProperties = {
  register?: UseFormRegister<Record<string, unknown>>
  name?: string
  options?: Array<string | SelectOption>
  searchable?: boolean
  placeholder?: string
} & SelectHTMLAttributes<HTMLSelectElement>

const Select = (properties: SelectProperties): JSX.Element => {
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
    setSelectedValue,
    isOpen,
    setIsOpen,
    toggleOpen,
    query,
    setQuery,
    listReference,
    handleKeyDown,
    highlightedIndex,
    setHighlightedIndex,
  } = useSelect({
    register,
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string | undefined,
    searchable,
  })

  const { rootReference } = useSelectUI({
    isOpen,
    close: () => setIsOpen(false),
    clearHighlight: () => setHighlightedIndex(-1),
  })

  // If no options specified and not searchable, fall back to native select for full compatibility
  if (!options && !searchable) {
    return <select className={selectStyle} {...rest} />
  }

  const selectedLabel =
    (selectedValue && filteredOptions.find((o) => o.value === selectedValue)?.label) ??
    placeholder ??
    ''

  return (
    <div ref={rootReference} className={`${className ?? selectStyle}`}>
      {/* Hidden native select kept for form integrations (RHF / native form submit) */}
      <select
        {...rest}
        {...registerProperties}
        name={name}
        value={selectedValue ?? rest.value}
        style={{ display: 'none' }}
      >
        {(normalizedOptions ?? []).map((opt) => (
          <option key={opt.value} value={opt.value}>
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
        onKeyDown={(event) => handleKeyDown(event.nativeEvent as KeyboardEvent)}
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
              onChange={(event) => setQuery(event.target.value)}
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
                key={opt.value}
                role="option"
                onClick={() => setSelectedValue(opt.value)}
                onMouseEnter={() => setHighlightedIndex(index)}
                onMouseLeave={() => setHighlightedIndex(-1)}
                className={
                  highlightedIndex === index ? `${option} ${optionHighlighted}` : option
                }
                data-value={opt.value}
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

export default Select
