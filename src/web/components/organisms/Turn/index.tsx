import { marked } from 'marked'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconCopy } from '@/components/atoms/IconCopy'
import { IconDelete } from '@/components/atoms/IconDelete'
import { IconEdit } from '@/components/atoms/IconEdit'
import { IconFork } from '@/components/atoms/IconFork'
import { Tooltip } from '@/components/molecules/Tooltip'
import { useTurnActions } from '@/components/organisms/Turn/hooks/useTurnActions'
import { useTurnHandlers } from '@/components/organisms/Turn/hooks/useTurnHandlers'
import { useTurnLifecycle } from '@/components/organisms/Turn/hooks/useTurnLifecycle'
import type { Turn } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import {
  turnHeader,
  turnHeaderInfo,
  turnIndexStyle,
  turnTimestamp,
  turnHeaderControls,
  turnContent,
  rawMarkdown,
  renderedMarkdown,
  toolResponseContent,
  statusSuccess,
  statusError,
  editablePre,
  editTextArea,
  editButtonContainer,
  editButtonIcon,
  turnWrapper,
  userTaskAligned,
  otherTurnAligned,
  turnContentBase,
  forkButtonIcon,
  deleteButtonIcon,
  copyButtonIcon
} from './style.css'

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

const Component = ({
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
  const {
    isEditing: lifecycleIsEditing,
    editedContent: lifecycleEditedContent,
    setIsEditing,
    setEditedContent
  } = useTurnLifecycle({ turn })

  const { deleteTurnAction, editTurnAction, forkSessionAction } = useTurnActions()

  const handlers = useTurnHandlers({
    turn,
    index,
    sessionId: sessionId || '',
    editedContent: lifecycleEditedContent,
    setIsEditing,
    setEditedContent,
    onRefresh: onRefresh || (async (): Promise<void> => {}),
    refreshSessionsInStore: refreshSessionsInStore || ((): void => {}),
    deleteTurnAction,
    editTurnAction,
    forkSessionAction
  })

  const isEditing = sessionId ? lifecycleIsEditing : propertyIsEditing
  const editedContent = sessionId ? lifecycleEditedContent : propertyEditedContent
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
    let markdownContent = ''
    let statusClass = ''

    if (isEditing) {
      return (
        <div className={turnContent}>
          <textarea
            className={editTextArea}
            value={editedContent}
            onChange={onEditedChange}
          />
          <div className={editButtonContainer}>
            <Button kind="primary" size="default" onClick={onSaveEdit}>
              Save
            </Button>
            <Button kind="secondary" size="default" onClick={onCancelEdit}>
              Cancel
            </Button>
          </div>
        </div>
      )
    }

    switch (turn.type) {
      case 'user_task':
        return <pre className={editablePre}>{turn.instruction || ''}</pre>
      case 'model_response':
      case 'compressed_history':
        markdownContent = turn.content || ''

        return (
          <div className={turnContent}>
            {turn.type === 'compressed_history' && (
              <p>
                <strong>
                  <em>-- History Compressed --</em>
                </strong>
              </p>
            )}
            <div className={rawMarkdown}>{markdownContent}</div>
            {!isStreaming && (
              <div
                className={`${renderedMarkdown} markdown-body`}
                dangerouslySetInnerHTML={{
                  __html: marked.parse(markdownContent.trim())
                }}
              />
            )}
          </div>
        )
      case 'function_calling':
        return (
          <pre className={turnContent}>{JSON.stringify(turn.response, null, 2)}</pre>
        )
      case 'tool_response':
        if (!turn.response) return null
        statusClass = turn.response.status === 'success' ? statusSuccess : statusError

        return (
          <div className={toolResponseContent}>
            <strong>Status: </strong>
            <span className={statusClass}>{turn.response.status}</span>
            {turn.response.output !== undefined && turn.response.output !== null && (
              <pre>{JSON.stringify(turn.response.output, null, 2)}</pre>
            )}
          </div>
        )
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
      className={`${turnWrapper} ${turn.type === 'user_task' ? userTaskAligned : otherTurnAligned}`}
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
              <Tooltip content="Fork Session">
                <Button kind="ghost" size="xsmall" onClick={onFork}>
                  <IconFork size={24} className={forkButtonIcon} />
                </Button>
              </Tooltip>
            )}
            {onCopy && (
              <Tooltip content="Copy Turn">
                <Button kind="ghost" size="xsmall" onClick={onCopy}>
                  <IconCopy size={24} className={copyButtonIcon} />
                </Button>
              </Tooltip>
            )}
            {expertMode &&
              (turn.type === 'user_task' || turn.type === 'model_response') &&
              onStartEdit && (
                <Tooltip content="Edit Turn">
                  <Button kind="ghost" size="xsmall" onClick={onStartEdit}>
                    <IconEdit size={24} className={editButtonIcon} />
                  </Button>
                </Tooltip>
              )}
            {onDelete && (
              <Tooltip content="Delete Turn">
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

// Export a named Turn component for consistency with the project's export rules
export const TurnComponent = Component

// Default export removed — use named export `TurnComponent`
