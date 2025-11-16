import type { JSX } from 'react'
import React, { useEffect, useRef } from 'react'

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
  list?: Item[]
  isMultiple?: boolean
  placeholder?: string
  onChange: (value: string[]) => void
  onFocus?: () => void
}

type PathDisplayProperties = {
  pathList: string[]
  onTagDelete: (index: number) => void
}

const PathDisplay = ({ pathList, onTagDelete }: PathDisplayProperties): JSX.Element => (
  <div className={pathDisplayContainer}>
    {pathList.map((path, index) => (
      <PathTag key={index} path={path} index={index} onDelete={onTagDelete} />
    ))}
  </div>
)

type SearchInputProperties = {
  value: string
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  onKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void
  onFocus?: () => void
  onClick?: () => void
  placeholder?: string
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProperties>(
  ({ value, onChange, onKeyDown, onFocus, onClick }, reference) => (
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
    />
  )
)

SearchInput.displayName = 'SearchInput'

export const FileSearchExplorer = ({
  existsValue,
  list,
  isMultiple = true,
  placeholder = 'Search...',
  onChange,
  onFocus
}: FileSearchExplorerProperties): JSX.Element => {
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)
  const handlers = useFileSearchExplorerHandlers(inputReference, {
    existsValue,
    list,
    isMultiple,
    onFocus,
    onChange
  })
  const {
    selectedValues,
    query,
    suggestions,
    selectedIndex,
    handleTagDelete,
    handleQueryChange,
    handleKeyDown,
    handleSuggestionClick,
    handleInputFocus,
    setSuggestions,
    setSelectedIndex
  } = handlers

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (
        inputReference.current &&
        suggestionListReference.current &&
        !inputReference.current.contains(event.target as Node) &&
        !suggestionListReference.current.contains(event.target as Node)
      ) {
        setSuggestions([])
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return (): void => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [setSuggestions, setSelectedIndex])

  return (
    <div className={container}>
      {suggestions.length > 0 &&
        (query.trim() !== '' || list !== undefined || query.trim() === '') && (
          <ul className={suggestionList} ref={suggestionListReference}>
            {suggestions.map((suggestion, index) => (
              <SuggestionItem
                key={index}
                suggestion={suggestion}
                onClick={handleSuggestionClick}
                isSelected={index === selectedIndex}
              />
            ))}
          </ul>
        )}
      <SearchInput
        ref={inputReference}
        value={query}
        onChange={handleQueryChange}
        onKeyDown={handleKeyDown}
        onFocus={handleInputFocus}
        onClick={handleInputFocus}
        placeholder={placeholder}
      />
      <PathDisplay pathList={selectedValues} onTagDelete={handleTagDelete} />
    </div>
  )
}
