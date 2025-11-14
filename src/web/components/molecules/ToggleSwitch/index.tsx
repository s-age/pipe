import clsx from 'clsx'
import type { JSX } from 'react'
import { useCallback } from 'react'

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
  checked?: boolean
  onChange?: (checked: boolean) => void
  disabled?: boolean
  label?: string
  ariaLabel?: string
}

export const ToggleSwitch = ({
  checked,
  onChange,
  disabled = false,
  label,
  ariaLabel
}: ToggleSwitchProperties): JSX.Element => {
  const { checked: isChecked, handleToggle } = useToggleSwitchHandlers({
    checked,
    onChange,
    disabled
  })

  const handleInputClick = useCallback((event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault()
  }, [])

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
