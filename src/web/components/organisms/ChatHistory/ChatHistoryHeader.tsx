import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { IconDelete } from '@/components/atoms/IconDelete'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { turnsHeader, deleteButton } from './style.css'

type ChatHistoryHeaderProperties = {
  sessionDetail: SessionDetail | null
  handleDeleteCurrentSession: () => void
  tokenCount?: number
  contextLimit?: number
}

export const ChatHistoryHeader = ({
  sessionDetail,
  handleDeleteCurrentSession,
  tokenCount: tokenCountProperty,
  contextLimit: contextLimitProperty
}: ChatHistoryHeaderProperties): JSX.Element => {
  const { state } = useSessionStore()
  // Prefer explicitly passed props (useful for Storybook/tests), then
  // session-specific values, then global store, then a safe default.
  const tokenCount = tokenCountProperty ?? sessionDetail?.token_count ?? 0
  const contextLimit =
    contextLimitProperty ??
    sessionDetail?.settings?.context_limit ??
    state.settings?.context_limit ??
    4000

  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  if (!sessionDetail) return <div />

  return (
    <div className={turnsHeader}>
      <Heading level={2}>
        {sessionDetail.purpose}{' '}
        {contextLimit > 0 && tokenCount !== null && `(${contextLeft}% context left)`}
      </Heading>
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
