import React from 'react'

import { useSuggestionItemHandlers } from './hooks/useSuggestionItemHandlers'
import { suggestionItem, selectedSuggestionItem } from './style.css'

export type SuggestionItemProperties = {
  suggestion: { label: string; value: string; path?: string }
  onClick: (suggestion: { label: string; value: string; path?: string }) => void
  isSelected?: boolean
}

export const SuggestionItem = React.memo(
  React.forwardRef<HTMLLIElement, SuggestionItemProperties>(
    ({ suggestion, onClick, isSelected = false }, reference) => {
      const { elementReference, handleClick } = useSuggestionItemHandlers(
        suggestion,
        onClick,
        isSelected,
        reference as React.RefObject<HTMLLIElement>
      )

      return (
        <li
          ref={elementReference}
          onClick={handleClick}
          className={isSelected ? selectedSuggestionItem : suggestionItem}
        >
          {suggestion.label}
        </li>
      )
    }
  )
)

SuggestionItem.displayName = 'SuggestionItem'
