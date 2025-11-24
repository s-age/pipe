import type { JSX } from 'react'
import React from 'react'

import { usePathTag } from './hooks/usePathTag'
import { pathTag, pathTagDeleteButton } from './style.css'

type PathTagProperties = {
  path: string
  index: number
  onDelete: (index: number) => void
}

export const PathTag = React.memo(
  ({ path, index, onDelete }: PathTagProperties): JSX.Element => {
    const { handleClick, handleKeyDown } = usePathTag({ index, onDelete })

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
