import type { JSX } from 'react'
import React from 'react'

import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { UnorderedList } from '@/components/molecules/UnorderedList'

import { useFileSearchExplorerHandlers } from './hooks/useFileSearchExplorerHandlers'
import { PathTag } from './PathTag'
import {
  container,
  pathDisplayContainer,
  searchInput,
  suggestionList
} from './style.css'
import { SuggestionItem } from './SuggestionItem'

type Item = {
  label: string
  value: string
  path?: string
}

type FileSearchExplorerProperties = {
  existsValue: string[]
  'aria-label'?: string
  isMultiple?: boolean
  list?: Item[]
  placeholder?: string
  onChange: (value: string[]) => void
  onFocus?: () => void
}

type PathDisplayProperties = {
  pathList: string[]
  onTagDelete: (index: number) => void
}

const PathDisplay = ({ pathList, onTagDelete }: PathDisplayProperties): JSX.Element => (
  <Flex wrap={true} gap="s" className={pathDisplayContainer}>
    {pathList.map((path, index) => (
      <PathTag key={index} path={path} index={index} onDelete={onTagDelete} />
    ))}
  </Flex>
)

type SearchInputProperties = {
  'aria-expanded': boolean
  'aria-controls': string
  value: string
  'aria-label'?: string
  'aria-activedescendant'?: string
  placeholder?: string
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  onKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void
  onClick?: () => void
  onFocus?: () => void
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProperties>(
  (
    {
      'aria-label': ariaLabel,
      'aria-expanded': ariaExpanded,
      'aria-controls': ariaControls,
      'aria-activedescendant': ariaActiveDescendant,
      onChange,
      onClick,
      onFocus,
      onKeyDown,
      value
    },
    reference
  ) => (
    <input
      ref={reference}
      type="text"
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      onFocus={onFocus}
      onClick={onClick}
      placeholder="Search files or directories..."
      className={searchInput}
      autoComplete="off"
      role="combobox"
      aria-autocomplete="list"
      aria-label={ariaLabel}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      aria-activedescendant={ariaActiveDescendant}
    />
  )
)

SearchInput.displayName = 'SearchInput'

export const FileSearchExplorer = ({
  existsValue,
  isMultiple = true,
  list,
  placeholder = 'Search...',
  onChange,
  onFocus,
  'aria-label': ariaLabel = 'Search files or directories'
}: FileSearchExplorerProperties): JSX.Element => {
  const {
    handleInputFocus,
    handleKeyDown,
    handleQueryChange,
    handleSuggestionClick,
    handleTagDelete,
    inputReference,
    query,
    selectedIndex,
    selectedValues,
    suggestionListReference,
    suggestions
  } = useFileSearchExplorerHandlers({
    existsValue,
    list,
    isMultiple,
    onFocus,
    onChange
  })

  const suggestionListId = 'file-search-suggestions'
  const isExpanded = suggestions.length > 0
  const activeDescendantId =
    isExpanded && selectedIndex >= 0
      ? `${suggestionListId}-option-${selectedIndex}`
      : undefined

  return (
    <Box className={container}>
      {isExpanded && (
        <UnorderedList
          className={suggestionList}
          ref={suggestionListReference}
          role="listbox"
          id={suggestionListId}
        >
          {suggestions.map((suggestion, index) => (
            <SuggestionItem
              key={index}
              id={`${suggestionListId}-option-${index}`}
              suggestion={suggestion}
              onClick={handleSuggestionClick}
              isSelected={index === selectedIndex}
            />
          ))}
        </UnorderedList>
      )}
      <SearchInput
        ref={inputReference}
        value={query}
        onChange={handleQueryChange}
        onKeyDown={handleKeyDown}
        onFocus={handleInputFocus}
        onClick={handleInputFocus}
        placeholder={placeholder}
        aria-label={ariaLabel}
        aria-expanded={isExpanded}
        aria-controls={suggestionListId}
        aria-activedescendant={activeDescendantId}
      />
      <PathDisplay pathList={selectedValues} onTagDelete={handleTagDelete} />
    </Box>
  )
}
