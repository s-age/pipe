import type { JSX } from 'react'

import { InstructionForm } from '@/components/organisms/InstructionForm'

import { newInstructionControl, footerForm } from './style.css'

type ChatHistoryFooterProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  isStreaming: boolean
  tokenCount?: number
  contextLimit?: number
}

export const ChatHistoryFooter = ({
  currentSessionId,
  onSendInstruction,
  isStreaming,
  tokenCount,
  contextLimit
}: ChatHistoryFooterProperties): JSX.Element => (
  <section className={newInstructionControl}>
    <div className={footerForm}>
      <InstructionForm
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
        tokenCount={tokenCount}
        contextLimit={contextLimit}
      />
    </div>
  </section>
)
