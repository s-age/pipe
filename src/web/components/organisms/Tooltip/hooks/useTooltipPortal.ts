import { useEffect, useRef } from 'react'

type UseTooltipPortalProperties = {
  isVisible: boolean
  placement: 'top' | 'bottom' | 'left' | 'right'
  targetRect: DOMRect | null
}

export const useTooltipPortal = ({
  isVisible,
  placement,
  targetRect
}: UseTooltipPortalProperties): React.RefObject<HTMLDivElement | null> => {
  const elementReference = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const node = elementReference.current
    if (!node || !targetRect) return

    // compute base coordinates
    const rect = targetRect
    let left = 0
    let top = 0
    let transform = ''

    if (placement === 'right') {
      left = Math.round(rect.right + 8)
      top = Math.round(rect.top + rect.height / 2)
      transform = 'translateY(-50%)'
    } else if (placement === 'left') {
      left = Math.round(rect.left - 8)
      top = Math.round(rect.top + rect.height / 2)
      transform = 'translate(-100%, -50%)'
    } else if (placement === 'bottom') {
      left = Math.round(rect.bottom + 8)
      top = Math.round(rect.left + rect.width / 2)
      transform = 'translateX(-50%)'
    } else {
      // top
      left = Math.round(rect.top - 8)
      top = Math.round(rect.left + rect.width / 2)
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
  }, [isVisible, placement, targetRect])

  return elementReference
}
