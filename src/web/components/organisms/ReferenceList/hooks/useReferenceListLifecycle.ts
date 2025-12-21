import { useEffect } from 'react'

const STORAGE_KEY = 'referenceListAccordionOpen'

export type UseReferenceListLifecycleProperties = {
  accordionOpen: boolean
}

/**
 * useReferenceListLifecycle
 *
 * Manages ReferenceList lifecycle effects (localStorage persistence).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useReferenceListLifecycle = ({
  accordionOpen
}: UseReferenceListLifecycleProperties): void => {
  // Persist accordion state to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(accordionOpen))
  }, [accordionOpen])
}
