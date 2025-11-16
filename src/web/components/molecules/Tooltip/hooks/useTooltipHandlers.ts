import { useCallback, useEffect, useRef, useState } from 'react'

import {
  emitTooltip,
  onTooltipClear,
  onTooltipHide,
  onTooltipShow
} from '../../../../lib/tooltipEvents'

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

  useEffect(() => {
    const offShow = onTooltipShow((data) => {
      if (!data || typeof data.id === 'undefined') return
      if (data.id === idReference.current) {
        // our tooltip was requested to show
        setPlacement((data.placement as TooltipPlacement) ?? 'top')
        setTargetRect((data.rect as DOMRect) ?? null)
        setIsVisible(true)
      } else {
        // some other tooltip shown -> hide ours
        setIsVisible(false)
      }
    })

    const offHide = onTooltipHide((data) => {
      if (!data || typeof data.id === 'undefined') return
      if (data.id === idReference.current) {
        setIsVisible(false)
        setTargetRect(null)
      }
    })

    const offClear = onTooltipClear(() => {
      setIsVisible(false)
      setTargetRect(null)
    })

    return (): void => {
      offShow()
      offHide()
      offClear()
    }
  }, [])

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

      // Emit show for this tooltip; include optional offsets/content
      emitTooltip.show({
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
    if (idReference.current !== null) emitTooltip.hide(idReference.current)
  }, [])

  return { isVisible, placement, targetRect, handleMouseEnter, handleMouseLeave }
}
