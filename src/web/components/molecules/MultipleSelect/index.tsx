import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'

import { useMultipleSelect } from './hooks/useMultipleSelect'
import type { SelectOption } from './hooks/useMultipleSelect'
import { useMultipleSelectHandlers } from './hooks/useMultipleSelectHandlers'
import {
  selectStyle,
  trigger,
  panel,
  option,
  optionHighlighted,
  searchInput,
  searchInputField,
  selectedTags,
  tag,
  tagRemove,
  checkbox
} from './style.css'
import { IconSearch } from '../../atoms/IconSearch'
import { useSelectUI } from '../Select/hooks/useSelectLifecycle'

type MultipleSelectProperties = {
  register?: UseFormRegister<Record<string, unknown>>
  name?: string
  options?: Array<string | SelectOption>
  searchable?: boolean
  placeholder?: string
} & SelectHTMLAttributes<HTMLSelectElement>

export const MultipleSelect = (properties: MultipleSelectProperties): JSX.Element => {
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
    selectedValues,
    isOpen,
    setIsOpen,
    query,
    setQuery,
    listReference,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValues
  } = useMultipleSelect({
    register,
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string[] | undefined,
    searchable
  })

  const {
    toggleOpen,
    handleRemoveTag,
    handleKeyDownReact,
    handleSearchChange,
    handleOptionClickReact,
    handleMouseEnterReact,
    handleMouseLeaveReact
  } = useMultipleSelectHandlers({
    isOpen,
    setIsOpen,
    filteredOptions,
    highlightedIndex,
    setHighlightedIndex,
    selectedValues,
    setSelectedValues,
    setQuery
  })

  const { rootReference } = useSelectUI({
    isOpen,
    close: () => setIsOpen(false),
    clearHighlight: () => setHighlightedIndex(-1)
  })

  const selectedLabels = selectedValues
    .map((value) => normalizedOptions.find((o) => o.value === value)?.label)
    .filter(Boolean)

  return (
    <div ref={rootReference} className={`${className ?? selectStyle}`}>
      {/* Hidden native select kept for form integrations (RHF / native form submit) */}
      <select
        {...rest}
        {...registerProperties}
        name={name}
        multiple={true}
        hidden={true}
      >
        {(normalizedOptions ?? []).map((opt) => (
          <option
            key={opt.value}
            value={opt.value}
            selected={selectedValues.includes(opt.value)}
          >
            {typeof opt.label === 'string' ? opt.label : String(opt.value)}
          </option>
        ))}
      </select>

      {/* Selected tags */}
      {selectedLabels.length > 0 && (
        <div className={selectedTags} onClick={handleRemoveTag}>
          {selectedLabels.map((label, index) => (
            <span key={selectedValues[index]} className={tag} data-index={index}>
              {label}
              <span className={tagRemove}>×</span>
            </span>
          ))}
        </div>
      )}

      <div
        tabIndex={0}
        role="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={toggleOpen}
        onKeyDown={handleKeyDownReact}
        className={trigger}
      >
        <span>
          {selectedLabels.length === 0
            ? (placeholder ?? 'Select options...')
            : `${selectedLabels.length} selected`}
        </span>
      </div>

      {isOpen && (
        <div>
          {searchable && (
            <div className={searchInput}>
              <IconSearch />
              <input
                type="text"
                value={query}
                onChange={handleSearchChange}
                placeholder="Search options..."
                className={searchInputField}
              />
            </div>
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
                onClick={handleOptionClickReact}
                onMouseEnter={handleMouseEnterReact}
                onMouseLeave={handleMouseLeaveReact}
                className={
                  highlightedIndex === index ? `${option} ${optionHighlighted}` : option
                }
                data-value={opt.value}
                data-index={String(index)}
              >
                <input
                  type="checkbox"
                  checked={selectedValues.includes(opt.value)}
                  readOnly={true}
                  className={checkbox}
                />
                {opt.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// (Removed temporary default export) Use named export `MultipleSelect`.
