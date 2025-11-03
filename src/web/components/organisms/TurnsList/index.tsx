import { useEffect, useRef, useState, JSX } from 'react'
import { ChangeEvent, KeyboardEvent } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import TextArea from '@/components/atoms/TextArea'
import Turn from '@/components/molecules/Turn'
import { TurnData, SessionData } from '@/lib/api/session/getSession'

import {
  turnsColumn,
  turnsHeader,
  turnsListSection,
  newInstructionControl,
  instructionTextarea,
  welcomeMessage,
} from './style.css'

type TurnsListProps = {
  sessionData: SessionData | null
  currentSessionId: string | null
  expertMode: boolean
  onDeleteTurn: (sessionId: string, turnIndex: number) => void
  onForkSession: (sessionId: string, forkIndex: number) => void
  onSendInstruction: (instruction: string) => void
  streamedText: string
  isStreaming: boolean
}

const TurnsList: ({
  sessionData,
  currentSessionId,
  expertMode,
  onDeleteTurn,
  onForkSession,
  onSendInstruction,
  streamedText,
  isStreaming,
}: TurnsListProps) => JSX.Element = ({
  sessionData,
  currentSessionId,
  expertMode,
  onDeleteTurn,
  onForkSession,
  onSendInstruction,
  streamedText,
  isStreaming,
}) => {
  const turnsListRef = useRef<HTMLDivElement>(null)
  const [instructionText, setInstructionText] = useState<string>('')

  const scrollToBottom = () => {
    if (turnsListRef.current) {
      turnsListRef.current.scrollTop = turnsListRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [sessionData, streamedText]) // sessionDataまたはstreamedTextが更新されたらスクロール

  const handleSend = async () => {
    if (!instructionText.trim() || !currentSessionId) return
    try {
      await onSendInstruction(instructionText)
      setInstructionText('')
    } catch (error) {
      console.error('Failed to send instruction:', error)
    }
  }

  if (!currentSessionId || !sessionData) {
    return (
      <div className={turnsColumn}>
        <div className={welcomeMessage}>
          <Heading level={1}>Welcome</Heading>
          <p>Select a session from the sidebar to view its details.</p>
        </div>
      </div>
    )
  }

  const contextLimit = 4000 // 仮の値
  const tokenCount = 1000 // 仮の値
  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  return (
    <div className={turnsColumn}>
      <div className={turnsHeader}>
        <Heading level={2} className={h2Style}>
          {sessionData.purpose}{' '}
          {contextLimit > 0 && tokenCount !== null && `(${contextLeft}% context left)`}
        </Heading>
        <Button
          kind="secondary"
          size="default"
          onClick={() => {
            /* onDeleteSession は HomePage で処理 */
          }}
        >
          Delete Session
        </Button>
      </div>

      <section className={turnsListSection} ref={turnsListRef}>
        {sessionData.turns.map((turn: TurnData, index: number) => (
          <Turn
            key={index}
            turn={turn}
            index={index}
            sessionId={currentSessionId}
            expertMode={expertMode}
            onDeleteTurn={onDeleteTurn}
            onForkSession={onForkSession}
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
            index={sessionData.turns.length} // 仮のインデックス
            sessionId={currentSessionId}
            expertMode={expertMode}
            onDeleteTurn={() => {}} // ストリーミング中は削除不可
            onForkSession={() => {}} // ストリーミング中はフォーク不可
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
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => {
            setInstructionText(e.target.value)
          }}
          onKeyPress={(e: KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          disabled={isStreaming} // ストリーミング中は無効化
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

export default TurnsList
