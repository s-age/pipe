import { useCallback, useEffect, useRef } from 'react'

export type SuggestionItemProperties = {
  suggestion: { label: string; value: string; path?: string }
  onClick: (suggestion: { label: string; value: string; path?: string }) => void
  isSelected?: boolean
}

export const useSuggestionItem = (
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

  return { elementReference, handleClick }
}
