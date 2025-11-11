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
  disabled: boolean
} => {
  const [internalChecked, setInternalChecked] = useState(externalChecked ?? false)

  const handleToggle = useCallback(() => {
    if (disabled) return
    const newChecked = !internalChecked
    setInternalChecked(newChecked)
    onChange?.(newChecked)
  }, [internalChecked, onChange, disabled])

  return {
    checked: externalChecked ?? internalChecked,
    handleToggle,
    disabled
  }
}
