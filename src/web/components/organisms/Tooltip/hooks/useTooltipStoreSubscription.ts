import { useEffect } from 'react'

import type { ActiveTooltip } from '@/stores/useTooltipStore'

import type { TooltipPlacement } from './useTooltipHandlers'

export type UseTooltipStoreSubscriptionProperties = {
  idReference: React.RefObject<number | null>
  setIsVisible: React.Dispatch<React.SetStateAction<boolean>>
  setPlacement: React.Dispatch<React.SetStateAction<TooltipPlacement>>
  setTargetRect: React.Dispatch<React.SetStateAction<DOMRect | null>>
  storeActive: ActiveTooltip
}

/**
 * useTooltipStoreSubscription
 *
 * Subscribes to tooltip store updates and syncs state.
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useTooltipStoreSubscription = ({
  idReference,
  setIsVisible,
  setPlacement,
  setTargetRect,
  storeActive
}: UseTooltipStoreSubscriptionProperties): void => {
  useEffect(() => {
    const data = storeActive

    if (!data || !data.id) {
      setIsVisible(false)
      setTargetRect(null)

      return
    }

    if (String(data.id) === String(idReference.current)) {
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
  }, [storeActive, idReference, setIsVisible, setPlacement, setTargetRect])
}
