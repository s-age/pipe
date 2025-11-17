import { useCallback, useEffect, useRef, useState } from 'react'

import { useTooltipStore, showTooltip, hideTooltip } from '@/stores/useTooltipStore'

export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right'

let nextTooltipId = 1

export const useTooltip = (): {
  isVisible: boolean
  placement: TooltipPlacement
  targetRect: DOMRect | null
  handleMouseEnter: (
    event: React.MouseEvent<HTMLElement>,
    options?: { content?: string; offsetMain?: number; offsetCross?: number }
  ) => void
  handleMouseLeave: () => void
} => {
  const [isVisible, setIsVisible] = useState(false)
  const [placement, setPlacement] = useState<TooltipPlacement>('top')
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null)

  // Unique id for this tooltip instance
  const idReference = useRef<number | null>(null)
  const store = useTooltipStore()

  useEffect(() => {
    const data = store.active

    if (!data) {
      setIsVisible(false)
      setTargetRect(null)

      return
    }

    if (data.id === idReference.current) {
      setPlacement((data.placement as TooltipPlacement) ?? 'top')
      setTargetRect((data.rect as DOMRect) ?? null)
      setIsVisible(true)
    } else {
      setIsVisible(false)
    }
  }, [store.active])

  const handleMouseEnter = useCallback(
    (
      event: React.MouseEvent<HTMLElement>,
      options?: { content?: string; offsetMain?: number; offsetCross?: number }
    ): void => {
      if (idReference.current === null) idReference.current = nextTooltipId++

      const { content, offsetMain, offsetCross } = options ?? {}

      const element = event.currentTarget as HTMLElement
      const rect = element.getBoundingClientRect()
      const vw = window.innerWidth
      const vh = window.innerHeight

      const spaceLeft = rect.left
      const spaceRight = vw - rect.right
      const maxHorizontal = Math.max(spaceLeft, spaceRight)

      const spaceTop = rect.top
      const spaceBottom = vh - rect.bottom
      const maxVertical = Math.max(spaceTop, spaceBottom)

      const chosenPlacement: TooltipPlacement =
        maxHorizontal > maxVertical
          ? spaceRight >= spaceLeft
            ? 'right'
            : 'left'
          : spaceBottom >= spaceTop
            ? 'bottom'
            : 'top'

      // Emit show to the tooltip store; include optional offsets/content
      showTooltip({
        id: idReference.current,
        rect,
        placement: chosenPlacement,
        content,
        offsetMain,
        offsetCross
      })
    },
    []
  )

  const handleMouseLeave = useCallback((): void => {
    if (idReference.current !== null) hideTooltip(idReference.current)
  }, [])

  return { isVisible, placement, targetRect, handleMouseEnter, handleMouseLeave }
}
