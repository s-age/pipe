import { clsx } from 'clsx'
import type { CSSProperties, JSX, ReactNode } from 'react'

import { grid } from './style.css'

type GridProperties = {
  children?: ReactNode
  columns?: '1' | '2' | '3' | '4' | 'auto-fit' | 'auto-fill' | string
  gap?: 's' | 'm' | 'l' | 'xl' | 'none'
  className?: string
}

const PRESET_COLUMNS = ['1', '2', '3', '4', 'auto-fit', 'auto-fill'] as const

export const Grid = ({
  children,
  columns = '1',
  gap = 'none',
  className,
  ...rest
}: GridProperties): JSX.Element => {
  const isPresetColumns = PRESET_COLUMNS.includes(columns as typeof PRESET_COLUMNS[number])

  const classNames = clsx(
    grid,
    {
      [`columns-${columns}`]: isPresetColumns,
      [`gap-${gap}`]: gap !== 'none'
    },
    className
  )

  const style: CSSProperties | undefined = !isPresetColumns
    ? { gridTemplateColumns: columns }
    : undefined

  return (
    <div className={classNames} style={style} {...rest}>
      {children}
    </div>
  )
}
