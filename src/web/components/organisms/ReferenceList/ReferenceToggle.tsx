import type { JSX } from 'react'
import { useCallback, useMemo, useRef } from 'react'

import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/molecules/Tooltip'
import type { Reference } from '@/types/reference'

type ReferenceToggleProperties = {
  index: number
  reference: Reference
  onToggle: (index: number) => void
}

export const ReferenceToggle = ({
  index,
  reference,
  onToggle
}: ReferenceToggleProperties): JSX.Element => {
  const timeoutReference = useRef<NodeJS.Timeout | null>(null)

  const debouncedOnToggle = useMemo(
    () =>
      (index: number): void => {
        if (timeoutReference.current) {
          clearTimeout(timeoutReference.current)
        }
        timeoutReference.current = setTimeout(() => onToggle(index), 100)
      },
    [onToggle]
  )

  const handleChange = useCallback(() => {
    debouncedOnToggle(index)
  }, [debouncedOnToggle, index])

  return (
    <Tooltip content="Toggle reference enabled">
      <ToggleSwitch
        checked={!reference.disabled}
        onChange={handleChange}
        ariaLabel={`Toggle reference ${reference.path} enabled`}
      />
    </Tooltip>
  )
}
