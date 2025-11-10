import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import { IconDelete } from '@/components/atoms/IconDelete'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { colors } from '@/styles/colors.css'

import { turnsHeader } from './style.css'

type ChatHistoryHeaderProperties = {
  sessionDetail: SessionDetail | null
  handleDeleteCurrentSession: () => void
}

export const ChatHistoryHeader = ({
  sessionDetail,
  handleDeleteCurrentSession
}: ChatHistoryHeaderProperties): JSX.Element => {
  const contextLimit = 4000
  const tokenCount = 1000
  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  if (!sessionDetail) return <div />

  return (
    <div className={turnsHeader}>
      <Heading level={2} className={h2Style}>
        {sessionDetail.purpose}{' '}
        {contextLimit > 0 && tokenCount !== null && `(${contextLeft}% context left)`}
      </Heading>
      <Button
        kind="secondary"
        size="default"
        onClick={handleDeleteCurrentSession}
        style={{ backgroundColor: colors.error, color: colors.lightText }}
      >
        <IconDelete size={16} />
      </Button>
    </div>
  )
}
