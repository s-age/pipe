import React from 'react'

import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'

import { useTabs } from './hooks/useTabs'
import * as styles from './style.css'

export type TabItem<K extends string = string> = {
  key: K
  label: string
}

export type TabsProperties<K extends string> = {
  activeKey: K
  tabs: TabItem<K>[]
  onChange: (key: K) => void
}

export const Tabs = <K extends string>({
  activeKey,
  tabs,
  onChange
}: TabsProperties<K>): React.ReactElement => {
  const { handleClick } = useTabs(onChange)

  return (
    <FlexColumn className={styles.tabsContainer}>
      <Flex className={styles.tabHeader} role="tablist">
        {tabs.map((t) => {
          const isActive = t.key === activeKey
          const className = isActive ? styles.tabButtonActive : styles.tabButton

          return (
            <button
              key={t.key}
              data-key={t.key}
              role="tab"
              aria-selected={isActive}
              className={className}
              onClick={handleClick}
            >
              {t.label}
            </button>
          )
        })}
      </Flex>

      <Box className={styles.tabPanel}>
        {/* panel content is controlled by parent via activeKey */}
      </Box>
    </FlexColumn>
  )
}
