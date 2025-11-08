import { useEffect, useRef } from 'react'
import type { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Heading from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import IconDelete from '@/components/atoms/IconDelete'
import IconPaperPlane from '@/components/atoms/IconPaperPlane'
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
  chatRoot,
  footerForm,
  instructionWrapper,
  overlaySendButton,
} from './style.css'

type ChatHistoryProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  expertMode: boolean
  setSessionDetail: (data: SessionDetail | null) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
}

type ChatHistoryLogicReturn = {
  streamedText: string | null
  isStreaming: boolean
  turnsListReference: React.RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  handleDeleteTurn: (sessionId: string, turnIndex: number) => Promise<void>
  handleForkSession: (sessionId: string, forkIndex: number) => Promise<void>
  handleDeleteSession: (sessionId: string) => Promise<void>
  onSendInstruction: (instruction: string) => Promise<void>
}

export const useChatHistoryLogic = ({
  currentSessionId,
  setSessionDetail,
  setError,
  refreshSessions,
}: Pick<
  ChatHistoryProperties,
  'currentSessionId' | 'setSessionDetail' | 'setError' | 'refreshSessions'
>): ChatHistoryLogicReturn => {
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

  // propagate streaming errors
  useEffect(() => {
    if (streamingError) {
      setError(streamingError)
      setStreamingTrigger(null)
    }
  }, [streamingError, setError, setStreamingTrigger])

  const turnsListReference = useRef<HTMLDivElement | null>(null)

  const scrollToBottom = (): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }

  return {
    streamedText,
    isStreaming,
    turnsListReference,
    scrollToBottom,
    handleDeleteTurn,
    handleForkSession,
    handleDeleteSession,
    onSendInstruction,
  }
}

export const ChatHistoryHeader = ({
  sessionDetail,
  currentSessionId,
  handleDeleteSession,
}: Pick<ChatHistoryProperties, 'sessionDetail' | 'currentSessionId'> & {
  handleDeleteSession: (id: string) => Promise<void>
}): JSX.Element => {
  if (!sessionDetail) return <div />

  const contextLimit = 4000
  const tokenCount = 1000
  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  return (
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
        <IconDelete size={16} />
      </Button>
    </div>
  )
}

export const ChatHistoryList = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  isStreaming,
  streamedText,
  turnsListReference,
  handleDeleteTurn,
  handleForkSession,
}: Pick<ChatHistoryProperties, 'sessionDetail' | 'currentSessionId' | 'expertMode'> & {
  isStreaming: boolean
  streamedText: string | null
  turnsListReference: React.RefObject<HTMLDivElement | null>
  handleDeleteTurn: (sessionId: string, turnIndex: number) => Promise<void>
  handleForkSession: (sessionId: string, forkIndex: number) => Promise<void>
}): JSX.Element => {
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

  return (
    <div className={turnsColumn}>
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
    </div>
  )
}

export const ChatHistoryFooter = ({
  currentSessionId,
  onSendInstruction,
  refreshSessions,
  setError,
  isStreaming,
}: {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  refreshSessions: () => Promise<void>
  setError: (message: string | null) => void
  isStreaming: boolean
}): JSX.Element => {
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
        <div className={instructionWrapper}>
          <TextArea
            id="new-instruction-text"
            className={instructionTextarea}
            placeholder="Enter your instruction here..."
            name="instruction"
            register={register}
            disabled={isStreaming}
            onKeyDown={(event: React.KeyboardEvent<HTMLTextAreaElement>) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                void submit()
              }
            }}
          />
          <Button
            className={overlaySendButton}
            kind="primary"
            size="default"
            onClick={() => void submit()}
            disabled={isStreaming}
            tabIndex={0}
            aria-label="Send Instruction"
          >
            <IconPaperPlane />
          </Button>
        </div>
      </>
    )
  }

  return (
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
        <div className={footerForm}>
          <InstructionForm />
        </div>
      </Form>
    </section>
  )
}

// Keep a default export for backward compatibility (renders the full composed view)
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
    turnsListReference,
    scrollToBottom,
    handleDeleteTurn,
    handleForkSession,
    handleDeleteSession,
    onSendInstruction,
  } = useChatHistoryLogic({
    currentSessionId,
    setSessionDetail,
    setError,
    refreshSessions,
  })

  useEffect(() => {
    scrollToBottom()
  }, [sessionDetail, streamedText, scrollToBottom])

  return (
    <div className={chatRoot}>
      <ChatHistoryHeader
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        handleDeleteSession={handleDeleteSession}
      />
      <ChatHistoryList
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        isStreaming={isStreaming}
        streamedText={streamedText}
        turnsListReference={turnsListReference}
        handleDeleteTurn={handleDeleteTurn}
        handleForkSession={handleForkSession}
      />
      <ChatHistoryFooter
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        refreshSessions={refreshSessions}
        setError={setError}
        isStreaming={isStreaming}
      />
    </div>
  )
}

export default ChatHistory
