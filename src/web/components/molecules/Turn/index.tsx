import { marked } from 'marked'
import { useState, JSX } from 'react'

import Button from '@/components/atoms/Button'
import Tooltip from '@/components/atoms/Tooltip'
import { Turn } from '@/lib/api/session/getSession'

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
  turnWrapper,
  userTaskAligned,
  otherTurnAligned,
  turnContentBase,
  materialIcons,
  forkButtonIcon,
  deleteButtonIcon,
  copyButtonIcon,
  editButtonIcon,
} from './style.css'

type TurnProps = {
  turn: Turn
  index: number
  sessionId: string
  expertMode: boolean
  onDeleteTurn: (sessionId: string, turnIndex: number) => void
  onForkSession: (sessionId: string, forkIndex: number) => void
  isStreaming?: boolean // 新しく追加
}

const Component = ({
  turn,
  index,
  sessionId,
  expertMode,
  onDeleteTurn,
  onForkSession,
  isStreaming = false,
}: TurnProps): JSX.Element => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content || turn.instruction || '',
  )

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

  const handleCopy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(editedContent)
      alert('Copied!')
    } catch (err) {
      console.error('Failed to copy: ', err)
      alert('Failed to copy')
    }
  }

  const handleSaveEdit = (): void => {
    // TODO: API呼び出しを実装する
    console.log(`Saving turn ${index} with new content: ${editedContent}`)
    setIsEditing(false)
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
            onChange={(e) => setEditedContent(e.target.value)}
          />
          <div className={editButtonContainer}>
            <Button kind="primary" size="default" onClick={handleSaveEdit}>
              Save
            </Button>
            <Button kind="secondary" size="default" onClick={() => setIsEditing(false)}>
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
                  __html: marked.parse(markdownContent.trim()),
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
            {turn.type === 'model_response' && (
              <Tooltip content="Fork Session">
                <Button
                  kind="ghost"
                  size="xsmall"
                  onClick={() => onForkSession(sessionId, index)}
                >
                  <span className={`${materialIcons} ${forkButtonIcon}`}>
                    call_split
                  </span>
                </Button>
              </Tooltip>
            )}
            <Tooltip content="Copy Turn">
              <Button kind="ghost" size="xsmall" onClick={handleCopy}>
                <span className={`${materialIcons} ${copyButtonIcon}`}>
                  content_copy
                </span>
              </Button>
            </Tooltip>
            {expertMode &&
              (turn.type === 'user_task' || turn.type === 'model_response') && (
                <Tooltip content="Edit Turn">
                  <Button kind="ghost" size="xsmall" onClick={() => setIsEditing(true)}>
                    <span className={`${materialIcons} ${editButtonIcon}`}>edit</span>
                  </Button>
                </Tooltip>
              )}
            <Tooltip content="Delete Turn">
              <Button
                kind="ghost"
                size="xsmall"
                onClick={() => onDeleteTurn(sessionId, index)}
              >
                <span className={`${materialIcons} ${deleteButtonIcon}`}>delete</span>
              </Button>
            </Tooltip>
          </div>
        </div>
        {renderTurnContent()}
      </div>
    </div>
  )
}

export default Component
