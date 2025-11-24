import { useState, useCallback } from 'react'

type UseToggleSwitchProperties = {
  checked?: boolean
  onChange?: (checked: boolean) => void
  disabled?: boolean
}

export const useToggleSwitchHandlers = ({
  checked: externalChecked,
  onChange,
  disabled = false
}: UseToggleSwitchProperties): {
  checked: boolean
  handleToggle: () => void
  handleInputClick: (event: React.MouseEvent<HTMLInputElement>) => void
  disabled: boolean
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
