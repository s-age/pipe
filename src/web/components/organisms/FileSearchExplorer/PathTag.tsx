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

    return (
      <span className={pathTag}>
        {path}
        <button onClick={handleClick} className={pathTagDeleteButton}>
          x
        </button>
      </span>
    )
  }
)

PathTag.displayName = 'PathTag'
