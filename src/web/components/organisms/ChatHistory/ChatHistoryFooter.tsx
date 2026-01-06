import type { JSX } from 'react'

import { InstructionForm } from '@/components/organisms/InstructionForm'

import { newInstructionControl, footerForm } from './style.css'

type ChatHistoryFooterProperties = {
  contextLimit: number
  currentSessionId: string | null
  isStreaming: boolean
  tokenCount?: number
  onSendInstruction: (instruction: string) => Promise<void>
  onRefresh?: () => Promise<void>
}

export const ChatHistoryFooter = ({
  contextLimit,
  currentSessionId,
  isStreaming,
  tokenCount,
  onSendInstruction,
  onRefresh
}: ChatHistoryFooterProperties): JSX.Element => (
  <section className={newInstructionControl}>
    <div className={footerForm}>
      <InstructionForm
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
        tokenCount={tokenCount}
        contextLimit={contextLimit}
        onRefresh={onRefresh}
      />
    </div>
  </section>
)
