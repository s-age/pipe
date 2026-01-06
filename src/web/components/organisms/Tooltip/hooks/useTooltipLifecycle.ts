import { useEffect, useRef } from 'react'

type UseTooltipLifecycleProperties = {
  isVisible: boolean
  placement: 'top' | 'bottom' | 'left' | 'right'
  targetRect: DOMRect | null
  offsetCross?: number | null
  offsetMain?: number | null
}

export const useTooltipLifecycle = ({
  isVisible,
  placement,
  targetRect,
  offsetCross,
  offsetMain
}: UseTooltipLifecycleProperties): React.RefObject<HTMLDivElement | null> => {
  const elementReference = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const node = elementReference.current
    if (!node) return

    // If the target rect is missing (e.g. the trigger unmounted or was removed),
    // ensure the portal is hidden so a stale tooltip doesn't remain visible.
    if (!targetRect) {
      node.style.visibility = 'hidden'
      node.style.opacity = '0'
      node.style.pointerEvents = 'none'

      return
    }

    // compute base coordinates
    const rect = targetRect
    let left = 0
    let top = 0
    let transform = ''

    const mainOffset = Number(offsetMain ?? 8)
    const crossOffset = Number(offsetCross ?? 0)

    if (placement === 'right') {
      left = Math.round(rect.right + mainOffset)
      top = Math.round(rect.top + rect.height / 2 + crossOffset)
      transform = 'translateY(-50%)'
    } else if (placement === 'left') {
      left = Math.round(rect.left - mainOffset)
      top = Math.round(rect.top + rect.height / 2 + crossOffset)
      transform = 'translate(-100%, -50%)'
    } else if (placement === 'bottom') {
      // Center horizontally under the element
      left = Math.round(rect.left + rect.width / 2 + crossOffset)
      top = Math.round(rect.bottom + mainOffset)
      transform = 'translateX(-50%)'
    } else {
      // top: center horizontally above the element
      left = Math.round(rect.left + rect.width / 2 + crossOffset)
      top = Math.round(rect.top - mainOffset)
      transform = 'translate(-50%, -100%)'
    }

    // Apply styles directly to DOM node to avoid JSX `style` prop (ESLint rule)
    node.style.position = 'absolute'
    node.style.left = `${left}px`
    node.style.top = `${top}px`
    node.style.transform = transform
    node.style.visibility = isVisible ? 'visible' : 'hidden'
    node.style.opacity = isVisible ? '1' : '0'
    // Prevent the tooltip from capturing pointer events so hovering into the portal
    // doesn't block mouseleave on the trigger element.
    node.style.pointerEvents = 'none'
  }, [isVisible, placement, targetRect, offsetMain, offsetCross])

  return elementReference
}
