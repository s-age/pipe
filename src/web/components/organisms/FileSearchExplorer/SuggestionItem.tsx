import React from 'react'

import { ListItem } from '@/components/molecules/ListItem'

import { useSuggestionItemHandlers } from './hooks/useSuggestionItemHandlers'
import { suggestionItem, selectedSuggestionItem } from './style.css'

export type SuggestionItemProperties = {
  id: string
  suggestion: { label: string; value: string; path?: string }
  isSelected?: boolean
  onClick: (suggestion: { label: string; value: string; path?: string }) => void
}

export const SuggestionItem = React.memo(
  React.forwardRef<HTMLLIElement, SuggestionItemProperties>(
    ({ id, isSelected = false, onClick, suggestion }, reference) => {
      const { elementReference, handleClick } = useSuggestionItemHandlers(
        suggestion,
        onClick,
        isSelected,
        reference as React.RefObject<HTMLLIElement>
      )

      return (
        <ListItem
          ref={elementReference}
          onClick={handleClick}
          className={isSelected ? selectedSuggestionItem : suggestionItem}
          role="option"
          id={id}
          aria-selected={isSelected}
        >
          {suggestion.label}
        </ListItem>
      )
    }
  )
)

SuggestionItem.displayName = 'SuggestionItem'
