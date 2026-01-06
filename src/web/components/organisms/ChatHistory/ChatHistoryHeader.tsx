import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { IconDelete } from '@/components/atoms/IconDelete'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { turnsHeader, deleteButton } from './style.css'

type ChatHistoryHeaderProperties = {
  sessionDetail: SessionDetail | null
  contextLimit?: number
  tokenCount?: number
  handleDeleteCurrentSession: () => void
}

export const ChatHistoryHeader = ({
  sessionDetail,
  handleDeleteCurrentSession
}: ChatHistoryHeaderProperties): JSX.Element => {
  if (!sessionDetail) return <div />

  return (
    <div className={turnsHeader}>
      <Heading level={2}>{sessionDetail.purpose}</Heading>
      <Button
        kind="secondary"
        size="default"
        onClick={handleDeleteCurrentSession}
        className={deleteButton}
      >
        <IconDelete size={16} />
      </Button>
    </div>
  )
}
