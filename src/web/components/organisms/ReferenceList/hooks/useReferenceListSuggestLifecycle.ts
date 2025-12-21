import { useEffect } from 'react'

export type UseReferenceListSuggestLifecycleProperties = {
  inputReference: React.RefObject<HTMLInputElement | null>
  suggestionListReference: React.RefObject<HTMLUListElement | null>
  setSuggestions: React.Dispatch<
    React.SetStateAction<{ name: string; isDirectory: boolean }[]>
  >
  setSelectedIndex: React.Dispatch<React.SetStateAction<number>>
}

/**
 * useReferenceListSuggestLifecycle
 *
 * Manages ReferenceListSuggest lifecycle effects (click outside detection).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useReferenceListSuggestLifecycle = ({
  inputReference,
  suggestionListReference,
  setSuggestions,
  setSelectedIndex
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
