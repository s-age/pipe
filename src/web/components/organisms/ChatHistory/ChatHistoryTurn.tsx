import type { JSX } from 'react'

import { TurnComponent as Turn } from '@/components/organisms/Turn'
import { useTurnHandlers } from '@/components/organisms/Turn/hooks/useTurnHandlers'
import type { Turn as TurnType } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useChatHistoryActions } from './hooks/useChatHistoryActions'
import { useChatHistoryHandlers } from './hooks/useChatHistoryHandlers'

type ChatHistoryTurnProperties = {
  turn: TurnType
  index: number
  currentSessionId: string
  expertMode: boolean
  onRefresh: () => Promise<void>
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

export const ChatHistoryTurn = ({
  turn,
  index,
  currentSessionId,
  expertMode,
  onRefresh,
  refreshSessionsInStore
}: ChatHistoryTurnProperties): JSX.Element => {
  const { deleteTurnAction, editTurnAction } = useChatHistoryActions({
    currentSessionId,
    refreshSessionsInStore
  })

  const { handleForkSession } = useChatHistoryHandlers({
    currentSessionId,
    refreshSessionsInStore
  })

  const {
    isEditing,
    editedContent,
    handleCopy,
    handleEditedChange,
    handleCancelEdit,
    handleStartEdit,
    handleFork,
    handleDelete,
    handleSaveEdit
  } = useTurnHandlers({
    turn,
    index,
    sessionId: currentSessionId,
    onRefresh,
    forkSessionAction: handleForkSession,
    deleteTurnAction,
    editTurnAction,
    onFork: handleForkSession
  })

  return (
    <Turn
      turn={turn}
      index={index}
      expertMode={expertMode}
      isEditing={isEditing}
      editedContent={editedContent}
      onCopy={handleCopy}
      onEditedChange={handleEditedChange}
      onCancelEdit={handleCancelEdit}
      onStartEdit={handleStartEdit}
      onFork={handleFork}
      onDelete={handleDelete}
      onSaveEdit={handleSaveEdit}
    />
  )
}
