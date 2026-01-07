import { useId, useState, useMemo, type KeyboardEvent } from 'react'

type UseAccordionProperties = {
  controlledOpen?: boolean
  defaultOpen?: boolean
  id?: string
  onOpenChange?: (open: boolean) => void
}

export const useAccordion = ({
  controlledOpen,
  defaultOpen = false,
  id,
  onOpenChange
}: UseAccordionProperties): {
  contentId: string
  open: boolean
  handleKeyDown: (event: KeyboardEvent) => void
  handleToggle: () => void
} => {
  const generatedId = useId()
  const contentId = useMemo(
    () => id ?? `accordion-content-${generatedId}`,
    [id, generatedId]
  )
  const [uncontrolledOpen, setUncontrolledOpen] = useState<boolean>(defaultOpen)

  // Determine whether to use controlled or uncontrolled mode
  const isControlled = controlledOpen !== undefined
  const open = isControlled ? controlledOpen : uncontrolledOpen

  const handleToggle = (): void => {
    if (isControlled) {
      onOpenChange?.(!open)
    } else {
      setUncontrolledOpen((s) => !s)
    }
  }

  const handleKeyDown = (event: KeyboardEvent): void => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleToggle()
    }
  }

  return {
    open,
    contentId,
    handleToggle,
    handleKeyDown
  }
}
