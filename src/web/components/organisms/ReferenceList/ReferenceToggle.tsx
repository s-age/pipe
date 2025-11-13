import type { JSX } from 'react'
import { useCallback } from 'react'

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
  const handleChange = useCallback(() => {
    onToggle(index)
  }, [onToggle, index])

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
