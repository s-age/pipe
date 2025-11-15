import type { JSX } from 'react'

import { TurnComponent as Turn } from '@/components/organisms/Turn'
import { useTurnHandlers } from '@/components/organisms/Turn/hooks/useTurnHandlers'
import type { Turn as TurnType } from '@/lib/api/session/getSession'

import { useChatHistoryActions } from './hooks/useChatHistoryActions'

type ChatHistoryTurnProperties = {
  turn: TurnType
  index: number
  currentSessionId: string
  expertMode: boolean
  onRefresh: () => Promise<void>
}

export const ChatHistoryTurn = ({
  turn,
  index,
  currentSessionId,
  expertMode,
  onRefresh
}: ChatHistoryTurnProperties): JSX.Element => {
  const { deleteTurnAction, forkSessionAction, editTurnAction } = useChatHistoryActions(
    {
      currentSessionId
    }
  )

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
    deleteTurnAction,
    forkSessionAction,
    editTurnAction
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
