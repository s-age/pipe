import React, { useCallback, useId, useMemo, useState } from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import { useOptionalFormContext } from '@/components/organisms/Form'

import * as styles from './style.css'

export type SliderProperties = Omit<
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

const Slider = (properties: SliderProperties): JSX.Element => {
  const {
    min = 0,
    max = 100,
    step = 1,
    value: controlledValue,
    defaultValue,
    onChange,
    register,
    name,
    id: idProperty,
    ...rest
  } = properties

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
  const internalValueReference = React.useRef<number>(internalValue)

  // We intentionally avoid synchronously calling setState inside an effect.
  // visibleValue derives directly from `controlledValue` when present, so
  // there's no need to update internal state from an effect. We keep the
  // internalValueRef for imperative updates from handleChange when uncontrolled.

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

  // We avoid mutating values returned from hooks. Instead, pass the registration
  // ref directly to the native input. React Hook Form supports either a callback
  // ref or a ref object returned from register(), so forwarding `registerProps.ref`
  // as the input ref is sufficient. When no registerProps are present we leave
  // the ref undefined.

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
          ref={
            (registerProperties as React.RefAttributes<HTMLInputElement>)?.ref ??
            undefined
          }
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
export default Slider
