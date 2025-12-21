import { useCallback, useRef } from 'react'

import { useSuggestionItemLifecycle } from './useSuggestionItemLifecycle'

export type SuggestionItemProperties = {
  suggestion: { label: string; value: string; path?: string }
  onClick: (suggestion: { label: string; value: string; path?: string }) => void
  isSelected?: boolean
}

export const useSuggestionItemHandlers = (
  suggestion: SuggestionItemProperties['suggestion'],
  onClick: SuggestionItemProperties['onClick'],
  isSelected: boolean = false,
  reference?: React.RefObject<HTMLLIElement>
): {
  elementReference: React.RefObject<HTMLLIElement | null>
  handleClick: () => void
} => {
  const internalReference = useRef<HTMLLIElement>(null)
  const elementReference = reference || internalReference

  // Lifecycle: scrollIntoView when selected
  useSuggestionItemLifecycle({ isSelected, elementReference })

  const handleClick = useCallback((): void => {
    onClick(suggestion)
  }, [onClick, suggestion])

  return { elementReference, handleClick }
}
