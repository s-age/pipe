import { useState, useEffect } from 'react'

const STORAGE_KEY = 'referenceListAccordionOpen'

type UseReferenceListLifecycleReturn = {
  accordionOpen: boolean
  setAccordionOpen: (open: boolean) => void
}

export const useReferenceListLifecycle = (
  _sessionId: string | null | undefined
): UseReferenceListLifecycleReturn => {
  const [accordionOpen, setAccordionOpen] = useState(() => {
    // Load from localStorage on initial mount
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY)

      return stored === 'true'
    }

    return false
  })

  // Persist accordion state to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(accordionOpen))
  }, [accordionOpen])

  return {
    accordionOpen,
    setAccordionOpen
  }
}
