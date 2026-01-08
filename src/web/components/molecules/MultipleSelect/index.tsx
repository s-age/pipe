import { clsx } from 'clsx'
import { type SelectHTMLAttributes, type JSX } from 'react'

import { IconSearch } from '@/components/atoms/IconSearch'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'

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
import { useSelectLifecycle } from '../Select/hooks/useSelectLifecycle'

type MultipleSelectProperties = {
  name: string
  options?: Array<string | SelectOption>
  placeholder?: string
  searchable?: boolean
} & SelectHTMLAttributes<HTMLSelectElement>

export const MultipleSelect = (properties: MultipleSelectProperties): JSX.Element => {
  const {
    className,
    name,
    options,
    placeholder,
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
    selectedValues,
    setHighlightedIndex,
    setIsOpen,
    setQuery,
    setSelectedValues
  } = useMultipleSelect({
    name,
    options: options ?? [],
    defaultValue: rest.defaultValue as string[] | undefined,
    searchable
  })

  // No debug logs in production code

  const {
    handleCheckboxClick,
    handleKeyDown,
    handleMouseEnter,
    handleMouseLeave,
    handleOptionClick,
    handleRemoveTag,
    handleSearchChange,
    toggleOpen
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

  // Generate stable IDs for ARIA attributes
  const listboxId = `${name}-listbox`
  const activeDescendantId =
    highlightedIndex >= 0 && filteredOptions[highlightedIndex]
      ? `${name}-option-${highlightedIndex}`
      : undefined

  const selectedLabels = selectedValues
    .map((value) => normalizedOptions.find((o) => o.value === value)?.label)
    .filter(Boolean)

  return (
    <Box ref={rootReference} className={clsx(selectStyle, className)}>
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
        <Flex className={selectedTags} onClick={handleRemoveTag}>
          {selectedLabels.map((label, index) => (
            <Box
              as="span"
              key={selectedValues[index]}
              className={tag}
              data-index={index}
            >
              {label}
              <Box as="span" className={tagRemove}>
                ×
              </Box>
            </Box>
          ))}
        </Flex>
      )}

      <Box
        tabIndex={0}
        role="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        aria-activedescendant={isOpen ? activeDescendantId : undefined}
        onClick={toggleOpen}
        onKeyDown={searchable ? undefined : handleKeyDown}
        className={trigger}
      >
        <Box as="span">
          {selectedLabels.length === 0
            ? (placeholder ?? 'Select options...')
            : `${selectedLabels.length} selected`}
        </Box>
      </Box>

      {isOpen && (
        <Box>
          {searchable && (
            <Box className={searchInput}>
              <IconSearch />
              <input
                type="text"
                value={query}
                onChange={handleSearchChange}
                onKeyDown={handleKeyDown}
                placeholder="Search options..."
                aria-label="Search options"
                aria-controls={listboxId}
                aria-activedescendant={activeDescendantId}
                aria-autocomplete="list"
                className={searchInputField}
                autoFocus={true}
              />
            </Box>
          )}

          <Box
            as="ul"
            id={listboxId}
            ref={listReference}
            role="listbox"
            aria-hidden={!isOpen}
            aria-multiselectable={true}
            className={panel}
          >
            {filteredOptions.map((opt, index) => {
              const isSelected = selectedValues.includes(opt.value)
              const optionId = `${name}-option-${index}`

              return (
                <Box
                  as="li"
                  id={optionId}
                  key={`${opt.value ?? ''}-${index}`}
                  role="option"
                  aria-selected={isSelected}
                  onClick={handleOptionClick}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                  className={clsx(
                    option,
                    highlightedIndex === index && optionHighlighted
                  )}
                  data-value={opt.value}
                  data-index={String(index)}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    readOnly={true}
                    className={checkbox}
                    value={opt.value}
                    onClick={handleCheckboxClick}
                    tabIndex={-1}
                    aria-hidden={true}
                  />
                  {opt.label}
                </Box>
              )
            })}
          </Box>
        </Box>
      )}
    </Box>
  )
}
