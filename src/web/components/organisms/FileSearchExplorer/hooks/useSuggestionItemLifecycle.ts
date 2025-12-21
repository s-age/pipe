import { useEffect } from 'react'

export type UseSuggestionItemLifecycleProperties = {
  isSelected: boolean
  elementReference: React.RefObject<HTMLLIElement | null>
}

/**
 * useSuggestionItemLifecycle
 *
 * Manages SuggestionItem lifecycle effects (scrollIntoView).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useSuggestionItemLifecycle = ({
  isSelected,
  elementReference
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
