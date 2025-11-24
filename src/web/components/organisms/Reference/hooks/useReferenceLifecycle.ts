import { useEffect, useState } from 'react'

import type { Reference } from '@/types/reference'

export const useReferenceLifecycle = (
  reference: Reference
): {
  localReference: Reference
  setLocalReference: React.Dispatch<React.SetStateAction<Reference>>
} => {
  const [localReference, setLocalReference] = useState(reference)

  // Update local state when prop changes
  useEffect(() => {
    setLocalReference(reference)
  }, [reference])

  return {
    localReference,
    setLocalReference
  }
}
