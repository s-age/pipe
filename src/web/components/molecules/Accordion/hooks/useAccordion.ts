import { useId, useState, type KeyboardEvent } from 'react'

type UseAccordionProperties = {
  id?: string
  defaultOpen?: boolean
}

export const useAccordion = ({
  id,
  defaultOpen = false
}: UseAccordionProperties): {
  open: boolean
  contentId: string
  handleToggle: () => void
  handleKeyDown: (event: KeyboardEvent) => void
} => {
  const generatedId = useId()
  const contentId = id ?? `accordion-content-${generatedId}`
  const [open, setOpen] = useState<boolean>(defaultOpen)

  const handleToggle = (): void => setOpen((s) => !s)

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
