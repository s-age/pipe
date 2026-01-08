import { useCallback, useRef, useState } from 'react'

import { useTooltipStore, showTooltip, hideTooltip } from '@/stores/useTooltipStore'

import { useTooltipStoreSubscription } from './useTooltipStoreSubscription'

export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right'

let nextTooltipId = 1

export const useTooltipHandlers = (
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
      offsetCross?: number
      offsetMain?: number
      placement?: TooltipPlacement
    }
  ) => void
  handleMouseLeave: () => void
  onEnter: (event: React.MouseEvent<HTMLElement>) => void
  onFocus: (event: React.FocusEvent<HTMLElement>) => void
  onBlur: () => void
  tooltipId: string | undefined
} => {
  const [isVisible, setIsVisible] = useState(false)
  const [placement, setPlacement] = useState<TooltipPlacement>('top')
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null)

  // Unique id for this tooltip instance
  const idReference = useRef<number | null>(null)
  const store = useTooltipStore()

  // Lifecycle: subscribe to tooltip store updates
  useTooltipStoreSubscription({
    idReference,
    storeActive: store.active,
    setIsVisible,
    setPlacement,
    setTargetRect
  })

  const handleMouseEnter = useCallback(
    (
      event: React.MouseEvent<HTMLElement>,
      options?: {
        content?: string
        offsetCross?: number
        offsetMain?: number
        placement?: TooltipPlacement
      }
    ): void => {
      if (idReference.current === null) idReference.current = nextTooltipId++

      const { content, offsetCross, offsetMain, placement } = options ?? {}

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

  const onFocus = useCallback(
    (event: React.FocusEvent<HTMLElement>) => {
      // Treat focus the same as mouse enter for accessibility
      handleMouseEnter(event as unknown as React.MouseEvent<HTMLElement>, {
        content,
        placement: forcedPlacement
      })
    },
    [handleMouseEnter, content, forcedPlacement]
  )

  const onBlur = useCallback(() => {
    handleMouseLeave()
  }, [handleMouseLeave])

  const tooltipId =
    idReference.current !== null ? `tooltip-${idReference.current}` : undefined

  return {
    isVisible,
    placement,
    targetRect,
    handleMouseEnter,
    handleMouseLeave,
    onEnter,
    onFocus,
    onBlur,
    tooltipId
  }
}
