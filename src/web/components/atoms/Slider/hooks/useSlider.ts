import { useCallback, useId, useMemo, useState, useRef, useEffect } from 'react'
import type { InputHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import { useOptionalFormContext } from '@/components/organisms/Form'

export type UseSliderProperties = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  'onChange' | 'type'
> & {
  min?: number
  max?: number
  step?: number
  value?: number
  defaultValue?: number
  onChange?: (value: number) => void
  register?: UseFormRegister<FieldValues>
  name?: string
}

export type UseSliderReturn = {
  id: string
  registerProperties?: UseFormRegisterReturn | undefined
  visibleValue: number
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  containerRef: (element: HTMLDivElement | null) => void
  // geometry
  svgWidth: number
  thumbR: number
  strokeWidth: number
  shadowPad: number
  pad: number
  trackX: number
  trackWidth: number
  fillWidth: number
  thumbCx: number
}

export const useSlider = ({
  min = 0,
  max = 100,
  step: _step = 1,
  value: controlledValue,
  defaultValue,
  onChange,
  register,
  name,
  id: idProperty,
}: UseSliderProperties): UseSliderReturn => {
  const fallbackId = useId()
  const id = idProperty ?? (name ? `${name}-slider` : `slider-${fallbackId}`)

  // obtain register from optional provider (safe; doesn't throw)
  const providerRegister: UseFormRegister<FieldValues> | undefined =
    useOptionalFormContext()?.register

  // memoize register props if available
  const registerProperties = useMemo<UseFormRegisterReturn | undefined>(() => {
    if (!name) return undefined
    if (register) return register(name)
    if (providerRegister) return providerRegister(name)

    return undefined
  }, [register, providerRegister, name])

  // internal state for uncontrolled usage
  const [internalValue, setInternalValue] = useState<number>(() => {
    if (typeof controlledValue === 'number') return controlledValue
    if (typeof defaultValue === 'number') return defaultValue

    return min
  })
  const internalValueReference = useRef<number>(internalValue)

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const v = Number(event.target.value)
      // call react-hook-form onChange if present (it expects the native event)
      try {
        registerProperties?.onChange?.(event as unknown as Event)
      } catch {
        // ignore
      }
      // update internal state if uncontrolled
      if (typeof controlledValue !== 'number') {
        setInternalValue(v)
        internalValueReference.current = v
      }
      onChange?.(v)
    },
    [onChange, registerProperties, controlledValue],
  )

  const visibleValue =
    typeof controlledValue === 'number' ? controlledValue : internalValue

  // measured width for responsive geometry (falls back to 300)
  const [measuredWidth, setMeasuredWidth] = useState<number>(300)
  const containerReference = useRef<HTMLDivElement | null>(null)

  useEffect((): (() => void) | undefined => {
    if (typeof window === 'undefined' || !('ResizeObserver' in window)) return undefined

    let rafId: number | null = null
    const ro = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (!entry) return
      const width = Math.max(0, Math.floor(entry.contentRect.width))
      // throttle to rAF
      if (rafId !== null) cancelAnimationFrame(rafId)
      rafId = requestAnimationFrame(() => {
        setMeasuredWidth(width || 300)
        rafId = null
      })
    })

    if (containerReference.current) ro.observe(containerReference.current)

    return (): void => {
      ro.disconnect()
      if (rafId !== null) cancelAnimationFrame(rafId)
    }
  }, [])

  const svgWidth = measuredWidth || 300
  const thumbR = 8
  const strokeWidth = 2
  const shadowPad = 2
  const pad = thumbR + strokeWidth / 2 + shadowPad
  const trackX = pad
  const trackWidth = svgWidth - 2 * pad
  const ratio = useMemo(
    () => Math.max(0, Math.min(1, (visibleValue - min) / (max - min || 1))),
    [visibleValue, min, max],
  )
  const fillWidth = ratio * trackWidth
  const thumbCx = trackX + fillWidth

  return {
    id,
    registerProperties,
    visibleValue,
    handleChange,
    containerRef: (element: HTMLDivElement | null): void => {
      containerReference.current = element
    },
    svgWidth,
    thumbR,
    strokeWidth,
    shadowPad,
    pad,
    trackX,
    trackWidth,
    fillWidth,
    thumbCx,
  }
}

// (Removed temporary default export) Use named export `useSlider`.
