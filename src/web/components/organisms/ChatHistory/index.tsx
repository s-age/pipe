import { useEffect, useRef } from 'react'
import type { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import TextArea from '@/components/atoms/TextArea'
import Turn from '@/components/molecules/Turn'
import { Form } from '@/components/organisms/Form'
import { useStreamingInstruction } from '@/components/pages/ChatHistoryPage/hooks/useStreamingInstruction'
import type { Turn as TurnType, SessionDetail } from '@/lib/api/session/getSession'
import { colors } from '@/styles/colors.css'

import useInstructionForm from './hooks/useInstructionForm'
import { useTurnActions } from './hooks/useTurnActions'
import {
  turnsColumn,
  turnsHeader,
  turnsListSection,
  newInstructionControl,
  instructionTextarea,
  welcomeMessage,
} from './style.css'

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

  const scrollToBottom = (): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [sessionDetail, streamedText])

  // InstructionForm hook encapsulates form context and submit/reset logic.
  const InstructionForm = (): JSX.Element => {
    const { register, submit } = useInstructionForm({
      currentSessionId,
      onSendInstruction,
      refreshSessions,
      setError,
    })

    return (
      <>
        <TextArea
          id="new-instruction-text"
          className={instructionTextarea}
          placeholder="Enter your instruction here..."
          name="instruction"
          register={register}
          disabled={isStreaming}
        />
        <Button
          kind="primary"
          size="default"
          onClick={() => void submit()}
          disabled={isStreaming}
        >
          {isStreaming ? 'Sending...' : 'Send Instruction'}
        </Button>
      </>
    )
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
        <Form
          onSubmit={async (data) => {
            const instruction = (data as { instruction?: string }).instruction ?? ''
            if (!instruction.trim() || !currentSessionId) return
            try {
              await onSendInstruction(instruction)
              await refreshSessions()
            } catch (error) {
              setError(
                error instanceof Error ? error.message : 'Failed to send instruction',
              )
              console.error('Failed to send instruction:', error)
            }
          }}
          defaultValues={{ instruction: '' }}
        >
          {/* InstructionForm uses the form context provided by Form */}
          <InstructionForm />
        </Form>
      </section>
    </div>
  )
}

export default ChatHistory
