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
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProperties>(
  ({ value, onChange, onKeyDown }, reference) => (
    <input
      ref={reference}
      type="text"
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      placeholder="Search files or directories..."
      className={searchInput}
      autoComplete="off"
    />
  )
)

SearchInput.displayName = 'SearchInput'

export const FileSearchExplorer = ({
  onPathChange
}: {
  onPathChange?: (paths: string[]) => void
} = {}): JSX.Element => {
  const inputReference = useRef<HTMLInputElement>(null)
  const handlers = useFileSearchExplorerHandlers(inputReference)
  const {
    pathList,
    query,
    suggestions,
    selectedIndex,
    handleTagDelete,
    handleQueryChange,
    handleKeyDown,
    handleSuggestionClick
  } = handlers

  useEffect(() => {
    console.log('FileSearchExplorer onPathChange called with:', pathList)
    onPathChange?.(pathList)
  }, [pathList, onPathChange])

  return (
    <div className={container}>
      {suggestions.length > 0 && (
        <ul className={suggestionList}>
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
      />
      <PathDisplay pathList={pathList} onTagDelete={handleTagDelete} />
    </div>
  )
}
