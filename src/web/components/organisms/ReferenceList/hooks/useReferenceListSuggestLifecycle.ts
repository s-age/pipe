import { useEffect } from 'react'

export type UseReferenceListSuggestLifecycleProperties = {
  inputReference: React.RefObject<HTMLInputElement | null>
  setSelectedIndex: React.Dispatch<React.SetStateAction<number>>
  setSuggestions: React.Dispatch<
    React.SetStateAction<{ isDirectory: boolean; name: string }[]>
  >
  suggestionListReference: React.RefObject<HTMLUListElement | null>
}

/**
 * useReferenceListSuggestLifecycle
 *
 * Manages ReferenceListSuggest lifecycle effects (click outside detection).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useReferenceListSuggestLifecycle = ({
  inputReference,
  setSelectedIndex,
  setSuggestions,
  suggestionListReference
}: UseReferenceListSuggestLifecycleProperties): void => {
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
  }, [inputReference, suggestionListReference, setSuggestions, setSelectedIndex])
}
