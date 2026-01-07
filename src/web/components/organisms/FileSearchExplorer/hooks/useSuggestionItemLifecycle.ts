import { useEffect } from 'react'

export type UseSuggestionItemLifecycleProperties = {
  elementReference: React.RefObject<HTMLLIElement | null>
  isSelected: boolean
}

/**
 * useSuggestionItemLifecycle
 *
 * Manages SuggestionItem lifecycle effects (scrollIntoView).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useSuggestionItemLifecycle = ({
  elementReference,
  isSelected
}: UseSuggestionItemLifecycleProperties): void => {
  useEffect(() => {
    if (isSelected && elementReference.current) {
      elementReference.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
      })
    }
  }, [isSelected, elementReference])
}
