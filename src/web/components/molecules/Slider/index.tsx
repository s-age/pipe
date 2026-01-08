import React from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { Label } from '@/components/atoms/Label'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { FlexColumn } from '@/components/molecules/FlexColumn'

import { useSliderHandlers } from './hooks/useSliderHandlers'
import * as styles from './style.css'

export type SliderProperties = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  'onChange' | 'type' | 'aria-label' | 'aria-orientation'
> & {
  'aria-label'?: string
  'aria-orientation'?: 'horizontal' | 'vertical'
  defaultValue?: number
  max?: number
  min?: number
  name?: string
  register?: UseFormRegister<FieldValues>
  step?: number
  value?: number
  onChange?: (value: number) => void
}

export const Slider = (properties: SliderProperties): JSX.Element => {
  const {
    'aria-label': ariaLabel,
    'aria-orientation': ariaOrientation = 'horizontal',
    defaultValue,
    max,
    min,
    name,
    onChange: _onChange,
    step,
    value,
    ...restProperties
  } = properties
  // intentionally reference the extracted `_onChange`, `value`, and `defaultValue` so linters know they're
  // intentionally excluded from `...restProperties` which is spread into the
  // native input (these are handled by useSlider hook instead).
  void _onChange
  void value
  void defaultValue

  const {
    containerRef,
    fillWidth,
    handleChange,
    id,
    registerProperties,
    svgWidth,
    thumbCx,
    thumbR,
    trackWidth,
    trackX,
    visibleValue
  } = useSliderHandlers(properties)

  return (
    <FlexColumn className={styles.container}>
      <Label htmlFor={id} className={styles.label}>
        <Text className={styles.valueLabel}>{visibleValue}</Text>
      </Label>

      <Box
        className={styles.trackWrap}
        ref={containerRef as unknown as React.Ref<HTMLDivElement>}
        data-value={visibleValue}
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
          data-value={visibleValue}
          onChange={handleChange}
          aria-label={ariaLabel}
          aria-valuemin={min}
          aria-valuemax={max}
          aria-valuenow={visibleValue}
          aria-orientation={ariaOrientation}
          {...restProperties}
        />
      </Box>
    </FlexColumn>
  )
}

// (Removed temporary default export) Use named export `Slider`.
