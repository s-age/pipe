import { useCallback, useState } from 'react'

export function useTooltip(): {
  isVisible: boolean
  handleMouseEnter: () => void
  handleMouseLeave: () => void
} {
  const [isVisible, setIsVisible] = useState(false)

  const handleMouseEnter = useCallback(() => setIsVisible(true), [])
  const handleMouseLeave = useCallback(() => setIsVisible(false), [])

  return { isVisible, handleMouseEnter, handleMouseLeave }
}
