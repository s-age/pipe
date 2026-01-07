import type { JSX } from 'react'

import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { useAppStore } from '@/stores/useAppStore'

import * as styles from './style.css'

export const LoadingOverlay = (): JSX.Element | null => {
  const { isLoading } = useAppStore()

  if (!isLoading) return null

  return (
    <Flex
      className={styles.overlay}
      role="status"
      aria-live="polite"
      aria-label="Loading"
      align="center"
      justify="center"
    >
      <Box className={styles.spinner} aria-hidden={true} />
      <Text className={styles.visuallyHidden}>Loading</Text>
    </Flex>
  )
}
