import type { JSX } from 'react'
import React from 'react'

import { Button } from '@/components/atoms/Button'
import { Text } from '@/components/atoms/Text'

import { usePathTagHandlers } from './hooks/usePathTagHandlers'
import { pathTag, pathTagDeleteButton } from './style.css'

type PathTagProperties = {
  index: number
  path: string
  onDelete: (index: number) => void
}

export const PathTag = React.memo(
  ({ index, path, onDelete }: PathTagProperties): JSX.Element => {
    const { handleClick, handleKeyDown } = usePathTagHandlers({ index, onDelete })

    return (
      <Button
        type="button"
        className={pathTag}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
      >
        <Text size="xs">{path}</Text>
        <Text size="xs" className={pathTagDeleteButton}>
          ×
        </Text>
      </Button>
    )
  }
)

PathTag.displayName = 'PathTag'
