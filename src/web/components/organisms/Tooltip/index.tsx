import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import { useTooltipStore } from '@/stores/useTooltipStore'

import { Tooltip } from './Tooltip'
import { TooltipPortal } from './TooltipPortal'

export const TooltipManager = (): JSX.Element | null => {
  const store = useTooltipStore()
  const activeTooltip = store.active

  if (typeof document === 'undefined') return null

  return createPortal(
    <>
      {activeTooltip ? (
        <TooltipPortal
          content={activeTooltip.content}
          isVisible={true}
          placement={activeTooltip.placement ?? 'top'}
          targetRect={activeTooltip.rect ?? null}
          offsetMain={activeTooltip.offsetMain}
          offsetCross={activeTooltip.offsetCross}
          tooltipId={activeTooltip.id ? `tooltip-${activeTooltip.id}` : undefined}
        />
      ) : null}
    </>,
    document.body
  )
}

// Re-export the molecule Tooltip here so consumers can import from
// `components/organisms/Tooltip` if they'd like a single import point.
export { Tooltip }
