import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'

import * as styles from './style.css'

type MetaLabelProperties = {
  children?: ReactNode
  required?: boolean
}

export const MetaLabel = ({
  children,
  required = false
}: MetaLabelProperties): JSX.Element => (
  <Box className={styles.label}>
    {children}
    {required && <Text className={styles.requiredMark}>*</Text>}
  </Box>
)

type MetaItemProperties = {
  children?: ReactNode
  className?: string
}

export const MetaItem = ({ children, className }: MetaItemProperties): JSX.Element => (
  <Box className={clsx(styles.wrapper, className)}>{children}</Box>
)

export type { MetaLabelProperties as MetaLabelProps }
