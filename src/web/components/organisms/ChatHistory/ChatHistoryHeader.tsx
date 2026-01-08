import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { IconDelete } from '@/components/atoms/IconDelete'
import { Flex } from '@/components/molecules/Flex'
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
}: ChatHistoryHeaderProperties): JSX.Element | null => {
  if (!sessionDetail) return null

  return (
    <Flex justify="between" align="center" className={turnsHeader}>
      <Heading level={2}>{sessionDetail.purpose}</Heading>
      <Button
        kind="secondary"
        size="default"
        onClick={handleDeleteCurrentSession}
        className={deleteButton}
        aria-label="Delete current session"
      >
        <IconDelete size={16} />
      </Button>
    </Flex>
  )
}
