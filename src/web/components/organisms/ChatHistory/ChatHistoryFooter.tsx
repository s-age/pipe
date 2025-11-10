import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconPaperPlane } from '@/components/atoms/IconPaperPlane'
import { TextArea } from '@/components/atoms/TextArea'
import { Form } from '@/components/organisms/Form'

import { useInstructionForm } from './hooks/useInstructionForm'
import {
  newInstructionControl,
  footerForm,
  instructionWrapper,
  instructionTextarea,
  overlaySendButton
} from './style.css'

const NOOP = (): void => {}

type ChatHistoryFooterProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
}

export const ChatHistoryFooter = ({
  currentSessionId,
  onSendInstruction,
  isStreaming
}: ChatHistoryFooterProperties): JSX.Element => (
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

type ChatHistoryInstructionFormProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
}

export const ChatHistoryInstructionForm = ({
  currentSessionId,
  onSendInstruction,
  isStreaming
}: ChatHistoryInstructionFormProperties): JSX.Element => {
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
