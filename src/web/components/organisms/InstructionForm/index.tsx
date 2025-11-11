import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconPaperPlane } from '@/components/atoms/IconPaperPlane'
import { TextArea } from '@/components/atoms/TextArea'
import { Form } from '@/components/organisms/Form'

import { useInstructionFormHandlers } from './hooks/useInstructionFormHandlers'
import { useInstructionFormLifecycle } from './hooks/useInstructionFormLifecycle'
import { instructionWrapper, instructionTextarea, overlaySendButton } from './style.css'

type InstructionFormProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
}

export const InstructionForm = ({
  currentSessionId,
  onSendInstruction,
  isStreaming
}: InstructionFormProperties): JSX.Element => {
  // We must call `useInstructionFormHandlers` inside the `Form` provider created by
  // `Form`. To ensure `useFormContext` is available we define an inner
  // component that consumes the context.
  const Inner = (): JSX.Element => {
    useInstructionFormLifecycle({ isStreaming })

    const { register, onTextAreaKeyDown, onSendClick } = useInstructionFormHandlers({
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

  // The Form component provides the form context. Form submission is handled
  // directly by the inner handlers (onTextAreaKeyDown/onSendClick) which call
  // the `submit` returned by `useInstructionFormHandlers`.
  return (
    <Form defaultValues={{ instruction: '' }}>
      <Inner />
    </Form>
  )
}
