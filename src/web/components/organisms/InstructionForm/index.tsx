import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconPaperPlane } from '@/components/atoms/IconPaperPlane'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { TextArea } from '@/components/molecules/TextArea'
import { Form } from '@/components/organisms/Form'

import { useInstructionFormHandlers } from './hooks/useInstructionFormHandlers'
import { useInstructionFormLifecycle } from './hooks/useInstructionFormLifecycle'
import {
  instructionWrapper,
  instructionTextarea,
  overlaySendButton,
  contextLeftText
} from './style.css'

type InstructionFormProperties = {
  contextLimit: number
  currentSessionId: string | null
  isStreaming: boolean
  tokenCount?: number
  onSendInstruction: (instruction: string) => Promise<void>
  onRefresh?: () => Promise<void>
}

export const InstructionForm = ({
  contextLimit: contextLimitProperty,
  currentSessionId,
  isStreaming,
  tokenCount: tokenCountProperty,
  onSendInstruction,
  onRefresh
}: InstructionFormProperties): JSX.Element => {
  // We must call `useInstructionFormHandlers` inside the `Form` provider created by
  // `Form`. To ensure `useFormContext` is available we define an inner
  // component that consumes the context.
  const Inner = (): JSX.Element => {
    const { onStopClick, register, submit } = useInstructionFormHandlers({
      currentSessionId,
      onSendInstruction,
      onRefresh
    })

    const tokenCount = tokenCountProperty ?? 0
    const { colorKey, contextLeft } = useInstructionFormLifecycle({
      isStreaming,
      tokenCount,
      contextLimit: contextLimitProperty
    })

    return (
      <FlexColumn>
        <Box className={instructionWrapper}>
          <TextArea
            id="new-instruction-text"
            className={instructionTextarea}
            placeholder="Enter your instruction here..."
            name="instruction"
            register={register}
            disabled={isStreaming}
          />
          {isStreaming ? (
            <Button
              className={overlaySendButton}
              kind="danger"
              size="default"
              onClick={onStopClick}
              tabIndex={0}
              aria-label="Stop Session"
            >
              ◽️
            </Button>
          ) : (
            <Button
              className={overlaySendButton}
              kind="primary"
              size="default"
              onClick={submit}
              tabIndex={0}
              aria-label="Send Instruction"
            >
              <IconPaperPlane />
            </Button>
          )}
        </Box>
        {contextLimitProperty > 0 && tokenCount !== null && (
          <Text className={contextLeftText[colorKey]} size="xs">
            {`(${contextLeft}% context left)`}
          </Text>
        )}
      </FlexColumn>
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
