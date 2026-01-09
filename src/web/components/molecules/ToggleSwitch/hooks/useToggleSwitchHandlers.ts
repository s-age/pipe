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

  const currentChecked = externalChecked ?? internalChecked

  const handleToggle = useCallback(() => {
    if (disabled) return
    const newChecked = !currentChecked
    setInternalChecked(newChecked)
    onChange?.(newChecked)
  }, [currentChecked, onChange, disabled])

  const handleInputClick = useCallback((event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault()
    event.stopPropagation()
  }, [])

  return {
    checked: currentChecked,
    handleToggle,
    handleInputClick,
    disabled
  }
}
