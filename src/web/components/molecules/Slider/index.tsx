import React from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useSlider } from './hooks/useSliderHandlers'
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

export const Slider = (properties: SliderProperties): JSX.Element => {
  const {
    onChange: _onChange,
    min,
    max,
    step,
    name,
    value,
    defaultValue,
    ...restProperties
  } = properties
  // intentionally reference the extracted `_onChange`, `value`, and `defaultValue` so linters know they're
  // intentionally excluded from `...restProperties` which is spread into the
  // native input (these are handled by useSlider hook instead).
  void _onChange
  void value
  void defaultValue

  const {
    id,
    registerProperties,
    visibleValue,
    handleChange,
    containerRef,
    svgWidth,
    thumbR,
    trackX,
    trackWidth,
    fillWidth,
    thumbCx
  } = useSlider(properties)

  return (
    <div className={styles.container}>
      <label htmlFor={id} className={styles.label}>
        <span className={styles.valueLabel}>{visibleValue}</span>
      </label>

      <div
        className={styles.trackWrap}
        ref={containerRef as unknown as React.Ref<HTMLDivElement>}
      >
        <svg className={styles.svg} viewBox={`0 0 ${svgWidth} 24`} aria-hidden={true}>
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
          id={id}
          ref={
            (registerProperties as unknown as React.RefAttributes<HTMLInputElement>)
              ?.ref ?? undefined
          }
          className={styles.hiddenRange}
          type="range"
          min={min}
          max={max}
          step={step}
          name={name}
          value={visibleValue}
          onChange={handleChange}
          {...restProperties}
        />
      </div>
    </div>
  )
}

// (Removed temporary default export) Use named export `Slider`.
