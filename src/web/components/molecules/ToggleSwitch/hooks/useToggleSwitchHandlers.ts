import { useState, useCallback } from 'react'

type UseToggleSwitchProperties = {
  checked?: boolean
  disabled?: boolean
  onChange?: (checked: boolean) => void
}

export const useToggleSwitchHandlers = ({
  checked: externalChecked,
  disabled = false,
  onChange
}: UseToggleSwitchProperties): {
  checked: boolean
  disabled: boolean
  handleInputClick: (event: React.MouseEvent<HTMLInputElement>) => void
  handleToggle: () => void
} => {
  const [internalChecked, setInternalChecked] = useState(externalChecked ?? false)

  const handleToggle = useCallback(() => {
    if (disabled) return
    const newChecked = !internalChecked
    setInternalChecked(newChecked)
    onChange?.(newChecked)
  }, [internalChecked, onChange, disabled])

  const handleInputClick = useCallback((event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault()
    event.stopPropagation()
  }, [])

  return {
    checked: externalChecked ?? internalChecked,
    handleToggle,
    handleInputClick,
    disabled
  }
}
