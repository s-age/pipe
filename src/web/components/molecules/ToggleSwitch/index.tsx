import clsx from 'clsx'
import type { JSX } from 'react'

import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'

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
    <Flex as="label" className={toggleSwitch} onClick={handleToggle} align="center">
      <input
        type="checkbox"
        className={toggleInput}
        checked={isChecked}
        disabled={disabled}
        aria-label={ariaLabel}
        onClick={handleInputClick}
      />
      <Box
        as="span"
        className={clsx(toggleSlider, {
          [toggleSliderChecked]: isChecked
        })}
      />
      {label && <Text className={toggleLabel}>{label}</Text>}
    </Flex>
  )
}
