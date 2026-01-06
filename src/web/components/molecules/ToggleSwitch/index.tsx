import clsx from 'clsx'
import type { JSX } from 'react'

import { Label } from '@/components/atoms/Label'

import { useToggleSwitchHandlers } from './hooks/useToggleSwitchHandlers'
import {
  toggleSwitch,
  toggleInput,
  toggleSlider,
  toggleSliderChecked,
  toggleLabel
} from './style.css'

type ToggleSwitchProperties = {
  ariaLabel?: string
  checked?: boolean
  disabled?: boolean
  label?: string
  onChange?: (checked: boolean) => void
}

export const ToggleSwitch = ({
  ariaLabel,
  checked,
  disabled = false,
  label,
  onChange
}: ToggleSwitchProperties): JSX.Element => {
  const {
    checked: isChecked,
    handleInputClick,
    handleToggle
  } = useToggleSwitchHandlers({
    checked,
    onChange,
    disabled
  })

  return (
    <label className={toggleSwitch} onClick={handleToggle}>
      <input
        type="checkbox"
        className={toggleInput}
        checked={isChecked}
        disabled={disabled}
        aria-label={ariaLabel}
        onClick={handleInputClick}
      />
      <span
        className={clsx(toggleSlider, {
          [toggleSliderChecked]: isChecked
        })}
      />
      {label && <Label className={toggleLabel}>{label}</Label>}
    </label>
  )
}
