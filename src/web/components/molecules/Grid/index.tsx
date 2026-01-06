import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { grid } from './style.css'

type GridProperties = {
  children?: ReactNode
  className?: string
  columns?: '1' | '2' | '3' | '4' | 'auto-fit' | 'auto-fill' | string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
}

const PRESET_COLUMNS = ['1', '2', '3', '4', 'auto-fit', 'auto-fill'] as const

export const Grid = ({
  children,
  className,
  columns = '1',
  gap = 'none',
  ...rest
}: GridProperties): JSX.Element => {
  const isPresetColumns = PRESET_COLUMNS.includes(
    columns as (typeof PRESET_COLUMNS)[number]
  )

  const classNames = clsx(
    grid,
    {
      [`columns-${columns}`]: isPresetColumns,
      'columns-custom': !isPresetColumns,
      [`gap-${gap}`]: gap !== 'none'
    },
    className
  )

  const customProperties = !isPresetColumns
    ? { '--grid-template-columns': columns }
    : undefined

  return (
    <div className={classNames} {...customProperties} {...rest}>
      {children}
    </div>
  )
}
