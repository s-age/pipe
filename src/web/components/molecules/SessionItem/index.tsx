import React from 'react'

import { Checkbox } from '@/components/atoms/Checkbox'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import { sessionItem, checkbox, content, subject } from './style.css'

type Properties = {
  session: SessionOverview | SessionTreeNode
  isSelected: boolean
  onSelect: (sessionId: string, isSelected: boolean) => void
}

export const SessionItem: React.FC<Properties> = ({
  session,
  isSelected,
  onSelect
}) => {
  const sessionId = session.session_id
  const sessionName =
    'purpose' in session
      ? session.purpose
      : (session.overview?.purpose as string) || 'Unknown'
  const createdAt =
    'last_update' in session
      ? session.last_update
      : (session.overview?.last_updated as string) || ''

  const formatDate = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  const createdAtDate = createdAt ? new Date(createdAt) : null
  const createdAtDisplay =
    createdAtDate && !isNaN(createdAtDate.getTime())
      ? formatDate(createdAtDate)
      : 'Unknown'

  const shortHash = sessionId.slice(0, 7)

  const { handleSelect } = useSessionItemHandlers(sessionId, isSelected, onSelect)

  return (
    <div className={sessionItem}>
      <Checkbox className={checkbox} checked={isSelected} onChange={handleSelect} />
      <div className={content}>
        <span className={subject}>{sessionName}</span>
        <span className={shortHash}>{shortHash}</span>
        <span className={createdAt}>{createdAtDisplay}</span>
      </div>
    </div>
  )
}
