import { type SelectHTMLAttributes, type JSX } from 'react'

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
import { useSelectLifecycle } from '../Select/hooks/useSelectLifecycle'

type MultipleSelectProperties = {
  name: string
  options?: Array<string | SelectOption>
  searchable?: boolean
  placeholder?: string
} & SelectHTMLAttributes<HTMLSelectElement>

export const MultipleSelect = (properties: MultipleSelectProperties): JSX.Element => {
  const {
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
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string[] | undefined,
    searchable
  })

  // No debug logs in production code

  const {
    toggleOpen,
    handleRemoveTag,
    handleKeyDown,
    handleSearchChange,
    handleOptionClick,
    handleMouseEnter,
    handleMouseLeave,
    handleCheckboxClick
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

  const { rootReference } = useSelectLifecycle({
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
        {(normalizedOptions ?? []).map((opt, index) => (
          <option key={`${opt.value ?? ''}-${index}`} value={opt.value}>
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
        onKeyDown={handleKeyDown}
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
                key={`${opt.value ?? ''}-${index}`}
                role="option"
                onClick={handleOptionClick}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
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
                  value={opt.value}
                  onClick={handleCheckboxClick}
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
