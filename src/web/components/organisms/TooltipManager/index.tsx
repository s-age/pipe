import type { JSX } from 'react'
import React, { useCallback, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

import { TooltipPortal } from '@/components/molecules/Tooltip/TooltipPortal'
import type { TooltipEventData } from '@/lib/tooltipEvents'
import { onTooltipShow, onTooltipHide, onTooltipClear } from '@/lib/tooltipEvents'

type TooltipEntry = {
  id: string
  content: React.ReactNode
  rect: DOMRect | null
  placement: 'top' | 'bottom' | 'left' | 'right'
}

export const TooltipManager = (): JSX.Element | null => {
  const [active, setActive] = useState<TooltipEntry | null>(null)

  const handleShow = useCallback((data: TooltipEventData): void => {
    const id = data.id ? String(data.id) : `tooltip-${Date.now()}`
    setActive({
      id,
      content: data.content ?? null,
      rect: data.rect ?? null,
      placement: data.placement ?? 'top'
    })
  }, [])

  const handleHide = useCallback((data: { id?: string | number }): void => {
    if (!data || data.id == null) {
      setActive(null)

      return
    }

    const id = String(data.id)
    setActive((s) => (s && s.id === id ? null : s))
  }, [])

  useEffect((): (() => void) => {
    const offShow = onTooltipShow(handleShow)
    const offHide = onTooltipHide(handleHide)
    const offClear = onTooltipClear(() => setActive(null))

    return (): void => {
      offShow()
      offHide()
      offClear()
    }
  }, [handleShow, handleHide])

  if (typeof document === 'undefined') return null

  return createPortal(
    <>
      {active ? (
        <TooltipPortal
          content={active.content}
          isVisible={true}
          placement={active.placement}
          targetRect={active.rect}
        />
      ) : null}
    </>,
    document.body
  )
}
