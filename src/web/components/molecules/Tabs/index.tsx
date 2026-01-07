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

/**
 * Props for the Tabs component.
 *
 * Note on accessibility:
 * - Tab buttons automatically include `aria-controls` pointing to panel IDs
 * - Panel ID format: `${ariaControlsPrefix}-panel-${key}` (default: "tab-panel-${key}")
 * - External panel elements should:
 *   - Use the matching panel ID format
 *   - Include `role="tabpanel"`
 *   - Include `aria-labelledby` pointing to the tab button ID (format: `${ariaControlsPrefix}-${key}`)
 *
 * @example
 * ```tsx
 * <Tabs activeKey="home" tabs={tabs} onChange={handleChange} />
 * // Corresponding panel:
 * <div id="tab-panel-home" role="tabpanel" aria-labelledby="tab-home">
 *   Panel content
 * </div>
 * ```
 */
export type TabsProperties<K extends string> = {
  activeKey: K
  tabs: TabItem<K>[]
  onChange: (key: K) => void
  /**
   * Prefix for generating tab and panel IDs.
   * Tab button ID: `${ariaControlsPrefix}-${key}`
   * Panel ID: `${ariaControlsPrefix}-panel-${key}`
   * @default "tab"
   */
  ariaControlsPrefix?: string
}

export const Tabs = <K extends string>({
  activeKey,
  tabs,
  onChange,
  ariaControlsPrefix = 'tab'
}: TabsProperties<K>): React.ReactElement => {
  const { handleClick } = useTabs(onChange)

  return (
    <FlexColumn className={styles.tabsContainer}>
      <Flex className={styles.tabHeader} role="tablist">
        {tabs.map((t) => {
          const isActive = t.key === activeKey
          const className = isActive ? styles.tabButtonActive : styles.tabButton
          const tabId = `${ariaControlsPrefix}-${t.key}`
          const panelId = `${ariaControlsPrefix}-panel-${t.key}`

          return (
            <button
              key={t.key}
              id={tabId}
              data-key={t.key}
              role="tab"
              aria-selected={isActive}
              aria-controls={panelId}
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
