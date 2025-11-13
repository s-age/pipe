import type { JSX } from 'react'
import React, { useCallback } from 'react'

import { pathTag, pathTagDeleteButton } from './style.css'

type PathTagProperties = {
  path: string
  index: number
  onDelete: (index: number) => void
}

export const PathTag = React.memo(
  ({ path, index, onDelete }: PathTagProperties): JSX.Element => {
    const handleClick = useCallback((): void => {
      onDelete(index)
    }, [onDelete, index])

    const handleKeyDown = useCallback(
      (event: React.KeyboardEvent<HTMLSpanElement>): void => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onDelete(index)
        }
      },
      [onDelete, index]
    )

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
