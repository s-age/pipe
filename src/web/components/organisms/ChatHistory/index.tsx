import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { h2Style } from '@/components/atoms/Heading/style.css'
import { IconDelete } from '@/components/atoms/IconDelete'
import { IconPaperPlane } from '@/components/atoms/IconPaperPlane'
import { TextArea } from '@/components/atoms/TextArea'
import { TurnComponent as Turn } from '@/components/molecules/Turn'
import { Form } from '@/components/organisms/Form'
import type { Turn as TurnType, SessionDetail } from '@/lib/api/session/getSession'
import { colors } from '@/styles/colors.css'

import { useChatHistoryHandlers } from './hooks/useChatHistoryHandlers'
import { useChatHistoryLogic } from './hooks/useChatHistoryLogic'
import { useInstructionForm } from './hooks/useInstructionForm'
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
  overlaySendButton
} from './style.css'

type ChatHistoryProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  expertMode: boolean
  setSessionDetail: (data: SessionDetail | null) => void
  onRefresh: () => Promise<void>
}

// useChatHistoryLogic を hooks フォルダに移動しました

const NOOP = (): void => {}

export const ChatHistoryHeader = ({
  sessionDetail,
  handleDeleteCurrentSession
}: Pick<ChatHistoryProperties, 'sessionDetail'> & {
  handleDeleteCurrentSession: () => void
}): JSX.Element => {
  const contextLimit = 4000
  const tokenCount = 1000
  const contextLeft = (((contextLimit - tokenCount) / contextLimit) * 100).toFixed(0)

  if (!sessionDetail) return <div />

  return (
    <div className={turnsHeader}>
      <Heading level={2} className={h2Style}>
        {sessionDetail.purpose}{' '}
        {contextLimit > 0 && tokenCount !== null && `(${contextLeft}% context left)`}
      </Heading>
      <Button
        kind="secondary"
        size="default"
        onClick={handleDeleteCurrentSession}
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
  onRefresh
}: Pick<ChatHistoryProperties, 'sessionDetail' | 'currentSessionId' | 'expertMode'> & {
  isStreaming: boolean
  streamedText: string | null
  turnsListReference: React.RefObject<HTMLDivElement | null>
  onRefresh: () => Promise<void>
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
        {((): JSX.Element[] => {
          const nodes: JSX.Element[] = []
          for (let i = 0; i < sessionDetail.turns.length; i += 1) {
            const turn: TurnType = sessionDetail.turns[i]
            nodes.push(
              <Turn
                key={i}
                turn={turn}
                index={i}
                sessionId={currentSessionId}
                expertMode={expertMode}
                onRefresh={onRefresh}
              />
            )
          }

          return nodes
        })()}
        {isStreaming && streamedText && (
          <Turn
            key="streaming-response"
            turn={{
              type: 'model_response',
              content: streamedText,
              timestamp: new Date().toISOString()
            }}
            index={sessionDetail.turns.length}
            sessionId={currentSessionId}
            expertMode={expertMode}
            onRefresh={onRefresh}
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
  isStreaming
}: {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
}): JSX.Element => (
  // The instruction form itself now owns the Form and submit handler to avoid
  // creating a new function reference in this component's render.
  <section className={newInstructionControl}>
    <div className={footerForm}>
      {}
      <ChatHistoryInstructionForm
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
      />
    </div>
  </section>
)

export const ChatHistoryInstructionForm = ({
  currentSessionId,
  onSendInstruction,
  isStreaming
}: {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
}): JSX.Element => {
  // We must call `useInstructionForm` inside the `Form` provider created by
  // `Form`. To ensure `useFormContext` is available we define an inner
  // component that consumes the context.
  const Inner = (): JSX.Element => {
    const { register, onTextAreaKeyDown, onSendClick } = useInstructionForm({
      currentSessionId,
      onSendInstruction
    })

    return (
      <div className={instructionWrapper}>
        <TextArea
          id="new-instruction-text"
          className={instructionTextarea}
          placeholder="Enter your instruction here..."
          name="instruction"
          register={register}
          disabled={isStreaming}
          onKeyDown={onTextAreaKeyDown}
        />
        <Button
          className={overlaySendButton}
          kind="primary"
          size="default"
          onClick={onSendClick}
          disabled={isStreaming}
          tabIndex={0}
          aria-label="Send Instruction"
        >
          <IconPaperPlane />
        </Button>
      </div>
    )
  }

  // The Form component provides the form context; we pass a no-op onSubmit
  // because the inner handlers (onTextAreaKeyDown/onSendClick) call the
  // `submit` returned by `useInstructionForm` directly. The no-op prevents
  // a double-submit when the user triggers a native form submit.
  return (
    <Form onSubmit={NOOP} defaultValues={{ instruction: '' }}>
      <Inner />
    </Form>
  )
}

// Keep a default export for backward compatibility (renders the full composed view)
export const ChatHistory = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  setSessionDetail,
  onRefresh
}: ChatHistoryProperties): JSX.Element => {
  const { handleDeleteCurrentSession } = useChatHistoryHandlers({
    currentSessionId
  })

  const { streamedText, isStreaming, turnsListReference, onSendInstruction } =
    useChatHistoryLogic({
      currentSessionId,
      // ChatHistory hook expects a loose setter type; cast to unknown to satisfy lint
      setSessionDetail: setSessionDetail as unknown as (data: unknown) => void
    })
  // scrolling handled in useChatHistoryLogic

  return (
    <div className={chatRoot}>
      <ChatHistoryHeader
        sessionDetail={sessionDetail}
        handleDeleteCurrentSession={handleDeleteCurrentSession}
      />
      <ChatHistoryList
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        isStreaming={isStreaming}
        streamedText={streamedText}
        turnsListReference={turnsListReference}
        onRefresh={onRefresh}
      />
      <ChatHistoryFooter
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
      />
    </div>
  )
}

// Default export removed — use named export `ChatHistory`
