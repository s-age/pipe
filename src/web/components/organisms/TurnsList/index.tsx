import { useEffect, useRef, useState, JSX } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import TextArea from '@/components/atoms/TextArea'
import Turn from '@/components/molecules/Turn'

import {
  turnsColumn,
  turnsHeader,
  turnsListSection,
  newInstructionControl,
  instructionTextarea,
  welcomeMessage,
} from './style.css'

type TurnData = {
  type: string
  content?: string
  instruction?: string
  response?: { status: string; output?: unknown }
  timestamp?: string
}

type SessionData = {
  purpose: string
  turns: TurnData[]
  // 他のsessionDataプロパティもここに追加
}

type TurnsListProps = {
  sessionData: SessionData | null
  currentSessionId: string | null
  expertMode: boolean
  onDeleteTurn: (sessionId: string, turnIndex: number) => void
  onForkSession: (sessionId: string, forkIndex: number) => void
  onSendInstruction: (sessionId: string, instruction: string) => void
}

const TurnsList: ({
  sessionData,
  currentSessionId,
  expertMode,
  onDeleteTurn,
  onForkSession,
  onSendInstruction,
}: TurnsListProps) => JSX.Element = ({
  sessionData,
  currentSessionId,
  expertMode,
  onDeleteTurn,
  onForkSession,
  onSendInstruction,
}) => {
  const turnsListRef = useRef<HTMLDivElement>(null)
  const [instructionText, setInstructionText] = useState<string>('')
  const [isSending, setIsSending] = useState<boolean>(false)

  const scrollToBottom = () => {
    if (turnsListRef.current) {
      turnsListRef.current.scrollTop = turnsListRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [sessionData]) // sessionDataが更新されたらスクロール

  const handleSend = async () => {
    if (!instructionText.trim() || !currentSessionId) return
    setIsSending(true)
    try {
      await onSendInstruction(currentSessionId, instructionText)
      setInstructionText('')
    } catch (error) {
      console.error('Failed to send instruction:', error)
    } finally {
      setIsSending(false)
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
      </section>

      <section className={newInstructionControl}>
        <TextArea
          id="new-instruction-text"
          className={instructionTextarea}
          placeholder="Enter your instruction here..."
          value={instructionText}
          onChange={(e) => setInstructionText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          disabled={isSending}
        />
        <Button kind="primary" size="default" onClick={handleSend} disabled={isSending}>
          {isSending ? 'Sending...' : 'Send Instruction'}
        </Button>
      </section>
    </div>
  )
}

export default TurnsList
