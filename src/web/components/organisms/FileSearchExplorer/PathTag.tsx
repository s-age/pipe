import type { JSX } from 'react'
import React from 'react'

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
      <span
        className={pathTag}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={handleKeyDown}
      >
        <span>{path}</span>
        <span className={pathTagDeleteButton}>×</span>
      </span>
    )
  }
)

PathTag.displayName = 'PathTag'
