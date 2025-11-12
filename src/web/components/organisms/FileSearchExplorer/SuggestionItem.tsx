import React, { useCallback, useEffect, useRef } from 'react'

import { suggestionItem, selectedSuggestionItem } from './style.css'

export type SuggestionItemProperties = {
  suggestion: string | { name: string; isDirectory: boolean }
  onClick: (suggestion: string | { name: string; isDirectory: boolean }) => void
  isSelected?: boolean
}

export const SuggestionItem = React.memo(
  React.forwardRef<HTMLLIElement, SuggestionItemProperties>(
    ({ suggestion, onClick, isSelected = false }, reference) => {
      const internalReference = useRef<HTMLLIElement>(null)
      const elementReference =
        (reference as React.RefObject<HTMLLIElement>) || internalReference

      useEffect(() => {
        if (isSelected && elementReference.current) {
          elementReference.current.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
          })
        }
      }, [isSelected, elementReference])

      const handleClick = useCallback((): void => {
        onClick(suggestion)
      }, [onClick, suggestion])

      return (
        <li
          ref={elementReference}
          onClick={handleClick}
          className={isSelected ? selectedSuggestionItem : suggestionItem}
        >
          {typeof suggestion === 'string'
            ? suggestion
            : suggestion.name + (suggestion.isDirectory ? '/' : '')}
        </li>
      )
    }
  )
)

SuggestionItem.displayName = 'SuggestionItem'
