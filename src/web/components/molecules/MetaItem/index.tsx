import type { JSX, ReactNode } from 'react'

import * as styles from './style.css'

type MetaLabelProperties = {
  children?: ReactNode
  required?: boolean
}

export const MetaLabel = ({
  children,
  required = false
}: MetaLabelProperties): JSX.Element => (
  <span className={styles.label}>
    {children}
    {required && <span className={styles.requiredMark}>*</span>}
  </span>
)

type MetaItemProperties = {
  children?: ReactNode
  className?: string
}

export const MetaItem = ({ children, className }: MetaItemProperties): JSX.Element => (
  <div className={`${styles.wrapper} ${className ?? ''}`.trim()}>{children}</div>
)

export type { MetaLabelProperties as MetaLabelProps }
