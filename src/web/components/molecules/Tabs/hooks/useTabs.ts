import React from 'react'

export const useTabs = <K extends string>(
  onChange: (key: K) => void
): {
  handleClick: (event: React.MouseEvent<HTMLButtonElement>) => void
} => {
  const handleClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>): void => {
      const key = event.currentTarget.dataset.key as K
      onChange(key)
    },
    [onChange]
  )

  return { handleClick }
}
