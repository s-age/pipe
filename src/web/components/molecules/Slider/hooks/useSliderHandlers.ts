import { useCallback, useId, useMemo, useState, useRef } from 'react'
import type { InputHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import { useOptionalFormContext } from '@/components/organisms/Form'

import { useSliderLifecycle } from './useSliderLifecycle'

export type UseSliderProperties = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  'onChange' | 'type'
> & {
  defaultValue?: number
  max?: number
  min?: number
  name?: string
  register?: UseFormRegister<FieldValues>
  step?: number
  value?: number
  onChange?: (value: number) => void
}

export type UseSliderReturn = {
  fillWidth: number
  id: string
  pad: number
  shadowPad: number
  strokeWidth: number
  svgWidth: number
  thumbCx: number
  thumbR: number
  trackWidth: number
  trackX: number
  visibleValue: number
  registerProperties?: UseFormRegisterReturn | undefined
  containerRef: (element: HTMLDivElement | null) => void
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void
}

export const useSliderHandlers = ({
  defaultValue,
  id: idProperty,
  max = 100,
  min = 0,
  name,
  onChange,
  register,
  step: _step = 1,
  value: controlledValue
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
        // Type guard: verify nativeEvent exists
        if (event.nativeEvent) {
          registerProperties?.onChange?.(event.nativeEvent)
        }
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
    [onChange, registerProperties, controlledValue]
  )

  const visibleValue =
    typeof controlledValue === 'number' ? controlledValue : internalValue

  // Lifecycle: ResizeObserver for responsive geometry
  const { containerRef: lifecycleContainerReference, measuredWidth } =
    useSliderLifecycle()

  const svgWidth = measuredWidth || 300
  const thumbR = 8
  const strokeWidth = 2
  const shadowPad = 2
  const pad = thumbR + strokeWidth / 2 + shadowPad
  const trackX = pad
  const trackWidth = svgWidth - 2 * pad
  const ratio = useMemo(
    () => Math.max(0, Math.min(1, (visibleValue - min) / (max - min || 1))),
    [visibleValue, min, max]
  )
  const fillWidth = ratio * trackWidth
  const thumbCx = trackX + fillWidth

  return {
    id,
    registerProperties,
    visibleValue,
    handleChange,
    containerRef: lifecycleContainerReference,
    svgWidth,
    thumbR,
    strokeWidth,
    shadowPad,
    pad,
    trackX,
    trackWidth,
    fillWidth,
    thumbCx
  }
}

// (Removed temporary default export) Use named export `useSlider`.
