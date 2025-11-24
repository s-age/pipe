import React from 'react'

import * as styles from './style.css'

export type TabItem<K extends string = string> = {
  key: K
  label: string
}

export type TabsProperties<K extends string> = {
  tabs: TabItem<K>[]
  activeKey: K
  onChange: (key: K) => void
}

export function Tabs<K extends string>({
  tabs,
  activeKey,
  onChange
}: TabsProperties<K>): React.ReactElement {
  const handleClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>): void => {
      const key = event.currentTarget.dataset.key as K
      onChange(key)
    },
    [onChange]
  )

  return (
    <div className={styles.tabsContainer}>
      <div className={styles.tabHeader} role="tablist">
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
      </div>

      <div className={styles.tabPanel}>
        {/* panel content is controlled by parent via activeKey */}
      </div>
    </div>
  )
}
