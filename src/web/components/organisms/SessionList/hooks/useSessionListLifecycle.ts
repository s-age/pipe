import { useRef, useEffect } from 'react'

export const useSessionListLifecycle = (
  allSelected: boolean,
  someSelected: boolean
): { checkboxRef: React.RefObject<HTMLInputElement | null> } => {
  const checkboxReference = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (checkboxReference.current) {
      checkboxReference.current.indeterminate = someSelected && !allSelected
    }
  }, [allSelected, someSelected])

  return {
    checkboxRef: checkboxReference
  }
}
