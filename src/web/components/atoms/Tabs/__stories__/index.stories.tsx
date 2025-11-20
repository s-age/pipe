import React from 'react'

import { Tabs, type TabItem } from '..'

export default {
  title: 'Atoms/Tabs',
  component: Tabs
}

export const Default = (): React.ReactElement => {
  const tabs: TabItem<DemoTab>[] = [
    { key: 'meta', label: 'Meta' },
    { key: 'compress', label: 'Compress' },
    { key: 'therapist', label: 'Therapist' }
  ]

  type DemoTab = 'meta' | 'compress' | 'therapist'
  const [active, setActive] = React.useState<DemoTab>('compress')

  const handleSetActive = (key: DemoTab): void => {
    setActive(key)
  }

  return (
    <div style={{ padding: 12 }}>
      <Tabs tabs={tabs} activeKey={active} onChange={handleSetActive} />
    </div>
  )
}
