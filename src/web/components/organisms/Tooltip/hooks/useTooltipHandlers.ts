import { useCallback, useEffect, useRef, useState } from 'react'

import { useTooltipStore, showTooltip, hideTooltip } from '@/stores/useTooltipStore'

export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right'

let nextTooltipId = 1

export const useTooltip = (
  content: string,
  forcedPlacement?: TooltipPlacement
): {
  isVisible: boolean
  placement: TooltipPlacement
  targetRect: DOMRect | null
  handleMouseEnter: (
    event: React.MouseEvent<HTMLElement>,
    options?: {
      content?: string
      offsetMain?: number
      offsetCross?: number
      placement?: TooltipPlacement
    }
  ) => void
  handleMouseLeave: () => void
  onEnter: (event: React.MouseEvent<HTMLElement>) => void
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
      // Type guard: verify placement is valid
      const validPlacement = data.placement ?? 'top'
      if (
        validPlacement === 'top' ||
        validPlacement === 'bottom' ||
        validPlacement === 'left' ||
        validPlacement === 'right'
      ) {
        setPlacement(validPlacement)
      } else {
        setPlacement('top')
      }

      // Type guard: verify rect is DOMRect
      if (data.rect instanceof DOMRect) {
        setTargetRect(data.rect)
      } else {
        setTargetRect(null)
      }
      setIsVisible(true)
    } else {
      setIsVisible(false)
    }
  }, [store.active])

  const handleMouseEnter = useCallback(
    (
      event: React.MouseEvent<HTMLElement>,
      options?: {
        content?: string
        offsetMain?: number
        offsetCross?: number
        placement?: TooltipPlacement
      }
    ): void => {
      if (idReference.current === null) idReference.current = nextTooltipId++

      const { content, offsetMain, offsetCross, placement } = options ?? {}

      const element = event.currentTarget

      // Type guard: verify element is HTMLElement
      if (!(element instanceof HTMLElement)) return

      const rect = element.getBoundingClientRect()
      const vw = window.innerWidth
      const vh = window.innerHeight

      const spaceLeft = rect.left
      const spaceRight = vw - rect.right
      const maxHorizontal = Math.max(spaceLeft, spaceRight)

      const spaceTop = rect.top
      const spaceBottom = vh - rect.bottom
      const maxVertical = Math.max(spaceTop, spaceBottom)

      const computedPlacement: TooltipPlacement =
        maxHorizontal > maxVertical
          ? spaceRight >= spaceLeft
            ? 'right'
            : 'left'
          : spaceBottom >= spaceTop
            ? 'bottom'
            : 'top'

      // Type guard: verify placement is valid
      let chosenPlacement: TooltipPlacement = computedPlacement
      if (
        placement === 'top' ||
        placement === 'bottom' ||
        placement === 'left' ||
        placement === 'right'
      ) {
        chosenPlacement = placement
      }

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

  const onEnter = useCallback(
    (event: React.MouseEvent<HTMLElement>) =>
      handleMouseEnter(event, { content, placement: forcedPlacement }),
    [handleMouseEnter, content, forcedPlacement]
  )

  return {
    isVisible,
    placement,
    targetRect,
    handleMouseEnter,
    handleMouseLeave,
    onEnter
  }
}
