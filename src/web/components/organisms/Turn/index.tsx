import { clsx } from 'clsx'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconCopy } from '@/components/atoms/IconCopy'
import { IconDelete } from '@/components/atoms/IconDelete'
import { IconEdit } from '@/components/atoms/IconEdit'
import { IconFork } from '@/components/atoms/IconFork'
import { Tooltip } from '@/components/organisms/Tooltip'
import { useTurnActions } from '@/components/organisms/Turn/hooks/useTurnActions'
import { useTurnHandlers } from '@/components/organisms/Turn/hooks/useTurnHandlers'
import type { Turn } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { EditingContent } from './EditingContent'
import { ModelResponseContent } from './ModelResponseContent'
import {
  turnHeader,
  turnHeaderInfo,
  turnIndexStyle,
  turnTimestamp,
  turnHeaderControls,
  turnContent,
  editButtonIcon,
  turnWrapper,
  userTaskAligned,
  otherTurnAligned,
  turnContentBase,
  forkButtonIcon,
  deleteButtonIcon,
  copyButtonIcon
} from './style.css'
import { ToolResponseContent } from './ToolResponseContent'
import { UserTaskContent } from './UserTaskContent'

type TurnProperties = {
  turn: Turn
  index: number
  expertMode: boolean
  isStreaming?: boolean
  // For ChatHistory integration
  sessionId?: string
  onRefresh?: () => Promise<void>
  refreshSessionsInStore?: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
  // Turn handlers passed from parent (for backward compatibility)
  isEditing?: boolean
  editedContent?: string
  onCopy?: () => Promise<void>
  onEditedChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
  onCancelEdit?: () => void
  onStartEdit?: () => void
  onFork?: () => void
  onDelete?: () => void
  onSaveEdit?: () => void
}

export const TurnComponent = ({
  turn,
  index,
  expertMode,
  isStreaming = false,
  sessionId,
  onRefresh,
  refreshSessionsInStore,
  isEditing: propertyIsEditing = false,
  editedContent: propertyEditedContent = '',
  onCopy: propertyOnCopy,
  onEditedChange: propertyOnEditedChange,
  onCancelEdit: propertyOnCancelEdit,
  onStartEdit: propertyOnStartEdit,
  onFork: propertyOnFork,
  onDelete: propertyOnDelete,
  onSaveEdit: propertyOnSaveEdit
}: TurnProperties): JSX.Element => {
  const { deleteTurnAction, editTurnAction, forkSessionAction } = useTurnActions()

  const handlers = useTurnHandlers({
    turn,
    index,
    sessionId: sessionId || '',
    onRefresh: onRefresh || (async (): Promise<void> => {}),
    refreshSessionsInStore: refreshSessionsInStore || ((): void => {}),
    deleteTurnAction,
    editTurnAction,
    forkSessionAction
  })

  const isEditing = sessionId ? handlers.isEditing : propertyIsEditing
  const editedContent = sessionId ? handlers.editedContent : propertyEditedContent
  const onCopy = handlers?.handleCopy ?? propertyOnCopy
  const onEditedChange = handlers?.handleEditedChange ?? propertyOnEditedChange
  const onCancelEdit = handlers?.handleCancelEdit ?? propertyOnCancelEdit
  const onStartEdit = handlers?.handleStartEdit ?? propertyOnStartEdit
  const onFork = handlers?.handleFork ?? propertyOnFork
  const onDelete = handlers?.handleDelete ?? propertyOnDelete
  const onSaveEdit = handlers?.handleSaveEdit ?? propertyOnSaveEdit
  const getHeaderContent = (type: string): string => {
    switch (type) {
      case 'user_task':
        return 'You'
      case 'model_response':
        return 'Model'
      case 'function_calling':
        return 'Function Calling'
      case 'tool_response':
        return 'Tool Response'
      case 'compressed_history':
        return 'Compressed'
      default:
        return 'Unknown'
    }
  }

  const renderTurnContent = (): JSX.Element | null => {
    if (isEditing) {
      return (
        <EditingContent
          editedContent={editedContent}
          onEditedChange={onEditedChange}
          onSaveEdit={onSaveEdit}
          onCancelEdit={onCancelEdit}
        />
      )
    }

    switch (turn.type) {
      case 'user_task':
        return <UserTaskContent instruction={turn.instruction || ''} />

      case 'model_response':
      case 'compressed_history':
        return (
          <ModelResponseContent
            content={turn.content || ''}
            isCompressed={turn.type === 'compressed_history'}
            isStreaming={isStreaming}
          />
        )

      case 'function_calling':
        return (
          <pre className={turnContent}>{JSON.stringify(turn.response, null, 2)}</pre>
        )

      case 'tool_response':
        if (!turn.response) return null

        return <ToolResponseContent response={turn.response} />

      default:
        return <pre className={turnContent}>{JSON.stringify(turn, null, 2)}</pre>
    }
  }

  const formatTimestamp = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  const timestamp = turn.timestamp ? formatTimestamp(new Date(turn.timestamp)) : ''

  return (
    <div
      className={clsx(
        turnWrapper,
        turn.type === 'user_task' ? userTaskAligned : otherTurnAligned
      )}
    >
      <div className={turnContentBase} id={`turn-${index}`}>
        <div className={turnHeader}>
          <span className={turnHeaderInfo}>
            <span className={turnIndexStyle}>{index + 1}:</span>
            {getHeaderContent(turn.type || 'unknown')}
            <span className={turnTimestamp}>{timestamp}</span>
          </span>
          <div className={turnHeaderControls}>
            {turn.type === 'model_response' && onFork && (
              <Tooltip content="Fork Session" placement="bottom">
                <Button kind="ghost" size="xsmall" onClick={onFork}>
                  <IconFork size={24} className={forkButtonIcon} />
                </Button>
              </Tooltip>
            )}
            {onCopy && (
              <Tooltip content="Copy Turn" placement="bottom">
                <Button kind="ghost" size="xsmall" onClick={onCopy}>
                  <IconCopy size={24} className={copyButtonIcon} />
                </Button>
              </Tooltip>
            )}
            {expertMode &&
              (turn.type === 'user_task' || turn.type === 'model_response') &&
              onStartEdit && (
                <Tooltip content="Edit Turn" placement="bottom">
                  <Button kind="ghost" size="xsmall" onClick={onStartEdit}>
                    <IconEdit size={24} className={editButtonIcon} />
                  </Button>
                </Tooltip>
              )}
            {expertMode && onDelete && (
              <Tooltip content="Delete Turn" placement="bottom">
                <Button kind="ghost" size="xsmall" onClick={onDelete}>
                  <IconDelete size={24} className={deleteButtonIcon} />
                </Button>
              </Tooltip>
            )}
          </div>
        </div>
        {renderTurnContent()}
      </div>
    </div>
  )
}
