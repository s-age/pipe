import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconPaperPlane } from '@/components/atoms/IconPaperPlane'
import { TextArea } from '@/components/molecules/TextArea'
import { Form } from '@/components/organisms/Form'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import { useInstructionFormHandlers } from './hooks/useInstructionFormHandlers'
import { useInstructionFormLifecycle } from './hooks/useInstructionFormLifecycle'
import {
  instructionWrapper,
  instructionTextarea,
  overlaySendButton,
  contextLeftText
} from './style.css'

type InstructionFormProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
  tokenCount?: number
  contextLimit?: number
}

export const InstructionForm = ({
  currentSessionId,
  onSendInstruction,
  isStreaming,
  tokenCount: tokenCountProperty,
  contextLimit: contextLimitProperty
}: InstructionFormProperties): JSX.Element => {
  // We must call `useInstructionFormHandlers` inside the `Form` provider created by
  // `Form`. To ensure `useFormContext` is available we define an inner
  // component that consumes the context.
  const Inner = (): JSX.Element => {
    const { register, onSendClick } = useInstructionFormHandlers({
      currentSessionId,
      onSendInstruction
    })

    const { state } = useSessionStore()
    const tokenCount = tokenCountProperty ?? 0
    const contextLimit = contextLimitProperty ?? state.settings?.context_limit ?? 700000
    const { contextLeft, colorKey } = useInstructionFormLifecycle({
      isStreaming,
      tokenCount,
      contextLimit
    })

    return (
      <div>
        <div className={instructionWrapper}>
          <TextArea
            id="new-instruction-text"
            className={instructionTextarea}
            placeholder="Enter your instruction here..."
            name="instruction"
            register={register}
            disabled={isStreaming}
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
        {contextLimit > 0 && tokenCount !== null && (
          <div className={contextLeftText[colorKey]}>({contextLeft}% context left)</div>
        )}
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
