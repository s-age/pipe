import type { JSX } from 'react'

import { SessionMeta } from '@/components/organisms/SessionMeta'
import type { SessionDetail } from '@/lib/api/session/getSession'

import * as styles from './style.css'
import { Tabs } from '../../molecules/Tabs'
import { Compressor } from '../Compressor'
import { Therapist } from '../Therapist'
import { useSessionControlHandlers } from './hooks/useSessionControlHandlers'
import type { SessionControlTab } from './hooks/useSessionControlHandlers'

export type SessionControlProperties = {
  sessionDetail: SessionDetail
  onRefresh: () => Promise<void>
  onSessionDetailUpdate?: (sessionDetail: SessionDetail) => void
}

export const SessionControl = ({
  sessionDetail,
  onRefresh,
  onSessionDetailUpdate
}: SessionControlProperties): JSX.Element => {
  const { active, handleTabChange } = useSessionControlHandlers()

  const tabs: { key: SessionControlTab; label: string }[] = [
    { key: 'meta', label: 'Meta' },
    { key: 'compress', label: 'Compressor' },
    { key: 'therapist', label: 'Therapist' }
  ]

  return (
    <div className={styles.rightColumn}>
      <Tabs tabs={tabs} activeKey={active} onChange={handleTabChange} />

      <div className={styles.metaBody}>
        {active === 'meta' && (
          <SessionMeta
            sessionDetail={sessionDetail}
            onRefresh={onRefresh}
            onSessionDetailUpdate={onSessionDetailUpdate}
          />
        )}

        {active === 'compress' && (
          <Compressor sessionDetail={sessionDetail} onRefresh={onRefresh} />
        )}

        {active === 'therapist' && (
          <Therapist sessionDetail={sessionDetail} onRefresh={onRefresh} />
        )}
      </div>
    </div>
  )
}
