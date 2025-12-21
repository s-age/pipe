import { useEffect } from 'react'

import type { Reference } from '@/types/reference'

export type UseReferenceLifecycleProperties = {
  reference: Reference
  setLocalReference: React.Dispatch<React.SetStateAction<Reference>>
}

/**
 * useReferenceLifecycle
 *
 * Manages Reference lifecycle effects (sync from props).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useReferenceLifecycle = ({
  reference,
  setLocalReference
}: UseReferenceLifecycleProperties): void => {
  // Update local state when prop changes
  useEffect(() => {
    setLocalReference(reference)
  }, [reference, setLocalReference])
}
