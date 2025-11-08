import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react'
import type { InputHTMLAttributes } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'
import { useFormContext } from '@/components/organisms/Form'
import * as styles from './style.css'

export type SliderProps = Omit<
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

export default function Slider(props: SliderProps) {
  const {
    min = 0,
    max = 100,
    step = 1,
    value: controlledValue,
    defaultValue,
    onChange,
    register,
    name,
    id: idProp,
    ...rest
  } = props

  const fallbackId = useId()
  const id = idProp ?? (name ? `${name}-slider` : `slider-${fallbackId}`)

  // try to obtain register from provider (may throw if not inside provider)
  let providerRegister: UseFormRegister<FieldValues> | undefined
  try {
    // useFormContext throws if no provider, so guard in try/catch
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    providerRegister = useFormContext()?.register
  } catch (err) {
    providerRegister = undefined
  }

  // memoize register props if available
  const registerProps = useMemo<UseFormRegisterReturn | undefined>(() => {
    if (!name) return undefined
    if (register) return register(name)
    if (providerRegister) return providerRegister(name)
    return undefined
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [register, providerRegister, name])

  // internal state for uncontrolled usage
  const [internalValue, setInternalValue] = useState<number>(() => {
    if (typeof controlledValue === 'number') return controlledValue
    if (typeof defaultValue === 'number') return defaultValue
    return min
  })

  // keep internal in sync with controlled prop
  useEffect(() => {
    if (typeof controlledValue === 'number') setInternalValue(controlledValue)
  }, [controlledValue])

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const v = Number(e.target.value)
      // call react-hook-form onChange if present (it expects the native event)
      try {
        registerProps?.onChange?.(e as unknown as Event)
      } catch (error) {
        // ignore
      }
      // update internal state if uncontrolled
      if (typeof controlledValue !== 'number') setInternalValue(v)
      onChange?.(v)
    },
    [onChange, registerProps, controlledValue],
  )

  // ref forwarding to satisfy register
  const localRef = useRef<HTMLInputElement | null>(null)
  useEffect(() => {
    if (!registerProps || !localRef.current) return
    try {
      if (typeof registerProps.ref === 'function') registerProps.ref(localRef.current)
      else if (registerProps.ref && 'current' in registerProps.ref)
        (registerProps.ref as any).current = localRef.current
    } catch (err) {
      // ignore
    }
  }, [registerProps])

  const visibleValue =
    typeof controlledValue === 'number' ? controlledValue : internalValue

  // SVG geometry constants to avoid thumb being clipped at the edges.
  // Add extra padding to account for stroke width and drop-shadow so thumb is never clipped (~2px observed).
  const svgWidth = 300
  const thumbR = 8
  const strokeWidth = 2 // matches thumb stroke in CSS
  const shadowPad = 2 // extra padding for drop-shadow
  const pad = thumbR + strokeWidth / 2 + shadowPad
  const trackX = pad
  const trackWidth = svgWidth - 2 * pad
  const ratio = Math.max(0, Math.min(1, (visibleValue - min) / (max - min || 1)))
  const fillWidth = ratio * trackWidth
  const thumbCx = trackX + fillWidth

  return (
    <div className={styles.container}>
      <label htmlFor={id} className={styles.label}>
        <span className={styles.valueLabel}>{visibleValue}</span>
      </label>

      <div className={styles.trackWrap}>
        <svg className={styles.svg} viewBox="0 0 300 24" aria-hidden>
          {/* track sits inside [thumbR, svgWidth - thumbR] so thumb never overflows */}
          <rect
            className={styles.track}
            x={trackX}
            y={10}
            width={trackWidth}
            height={4}
            rx={2}
          />
          <rect
            className={styles.fill}
            x={trackX}
            y={10}
            width={String(fillWidth)}
            height={4}
            rx={2}
          />
          {/* single circular thumb positioned inside the inner track */}
          <circle className={styles.thumbCircle} cx={thumbCx} cy={12} r={thumbR} />
        </svg>

        {/* Native range input: overlayed (transparent) to preserve native pointer/keyboard behavior and to integrate with forms/RHF */}
        <input
          {...rest}
          id={id}
          ref={localRef}
          className={styles.hiddenRange}
          type="range"
          min={min}
          max={max}
          step={step}
          name={name}
          value={visibleValue}
          onChange={handleChange}
        />
      </div>
    </div>
  )
}
