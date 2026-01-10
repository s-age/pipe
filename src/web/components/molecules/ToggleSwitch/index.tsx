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

const dumyyHandle = (): void => {
  // onChange is handled by the parent label's onClick
  // This empty handler satisfies React's controlled component requirements
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
    handleKeyDown,
    handleToggle
  } = useToggleSwitchHandlers({
    checked,
    onChange,
    disabled
  })

  return (
    <Flex
      as="label"
      className={toggleSwitch}
      onClick={handleToggle}
      onKeyDown={handleKeyDown}
      align="center"
      role="switch"
      aria-checked={isChecked}
      aria-label={ariaLabel}
      tabIndex={disabled ? -1 : 0}
    >
      <input
        type="checkbox"
        className={toggleInput}
        checked={isChecked}
        disabled={disabled}
        aria-hidden="true"
        onClick={handleInputClick}
        onChange={dumyyHandle}
        tabIndex={-1}
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
