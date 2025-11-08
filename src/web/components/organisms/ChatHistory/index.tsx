import { useEffect, useRef, useState } from 'react'
import type { JSX } from 'react'
import type { ChangeEvent, KeyboardEvent } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import TextArea from '@/components/atoms/TextArea'
import Turn from '@/components/molecules/Turn'
import type { Turn as TurnType, SessionDetail } from '@/lib/api/session/getSession'
import { colors } from '@/styles/colors.css'

import { useTurnActions } from './hooks/useTurnActions'
import {
  turnsColumn,
  turnsHeader,
  turnsListSection,
  newInstructionControl,
  instructionTextarea,
  welcomeMessage,
} from './style.css'
import { useStreamingInstruction } from '../../pages/ChatHistoryPage/hooks/useStreamingInstruction'

type ChatHistoryProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  expertMode: boolean
  setSessionDetail: (data: SessionDetail | null) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
}

const ChatHistory = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  setSessionDetail,
  setError,
  refreshSessions,
}: ChatHistoryProperties): JSX.Element => {
  const {
    streamedText,
    isStreaming,
    streamingError,
    onSendInstruction,
    setStreamingTrigger,
  } = useStreamingInstruction(currentSessionId, setSessionDetail)

  const { handleDeleteTurn, handleForkSession, handleDeleteSession } = useTurnActions(
    setError,
    refreshSessions,
  )

  // ストリーミングエラーをHomePageのerror状態に反映
  useEffect(() => {
    if (streamingError) {
      setError(streamingError)
      setStreamingTrigger(null)
    }
  }, [streamingError, setError, setStreamingTrigger])

  const turnsListReference = useRef<HTMLDivElement>(null)
  const [instructionText, setInstructionText] = useState<string>('')

  const scrollToBottom = (): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [sessionDetail, streamedText])

  const handleSend = async (): Promise<void> => {
    if (!instructionText.trim() || !currentSessionId) return
    try {
      await onSendInstruction(instructionText)
      await refreshSessions()
      setInstructionText('')
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to send instruction')
      console.error('Failed to send instruction:', error)
    }
  }

  if (!currentSessionId || !sessionDetail) {
    return (
      <div className={turnsColumn}>
        <div className={welcomeMessage}>
          <Heading level={1}>Welcome</Heading>
          <p>Select a session from the sidebar to view its details.</p>
        </div>
      </div>
    )
  }

  const contextLimit = 4000
  const tokenCount = 1000
  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  return (
    <div className={turnsColumn}>
      <div className={turnsHeader}>
        <Heading level={2} className={h2Style}>
          {sessionDetail.purpose}{' '}
          {contextLimit > 0 && tokenCount !== null && `(${contextLeft}% context left)`}
        </Heading>
        <Button
          kind="secondary"
          size="default"
          onClick={() => currentSessionId && handleDeleteSession(currentSessionId)}
          style={{ backgroundColor: colors.error, color: colors.lightText }}
        >
          Delete Session
        </Button>
      </div>

      <section className={turnsListSection} ref={turnsListReference}>
        {sessionDetail.turns.map((turn: TurnType, index: number) => (
          <Turn
            key={index}
            turn={turn}
            index={index}
            sessionId={currentSessionId}
            expertMode={expertMode}
            onDeleteTurn={handleDeleteTurn}
            onForkSession={handleForkSession}
          />
        ))}
        {isStreaming && streamedText && (
          <Turn
            key="streaming-response"
            turn={{
              type: 'model_response',
              content: streamedText,
              timestamp: new Date().toISOString(),
            }}
            index={sessionDetail.turns.length}
            sessionId={currentSessionId}
            expertMode={expertMode}
            onDeleteTurn={() => {}}
            onForkSession={() => {}}
            isStreaming={isStreaming}
          />
        )}
      </section>

      <section className={newInstructionControl}>
        <TextArea
          id="new-instruction-text"
          className={instructionTextarea}
          placeholder="Enter your instruction here..."
          value={instructionText}
          onChange={(event: ChangeEvent<HTMLTextAreaElement>) => {
            setInstructionText(event.target.value)
          }}
          onKeyPress={(event: KeyboardEvent<HTMLTextAreaElement>) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              handleSend()
            }
          }}
          disabled={isStreaming}
        />
        <Button
          kind="primary"
          size="default"
          onClick={handleSend}
          disabled={isStreaming}
        >
          {isStreaming ? 'Sending...' : 'Send Instruction'}
        </Button>
      </section>
    </div>
  )
}

export default ChatHistory
