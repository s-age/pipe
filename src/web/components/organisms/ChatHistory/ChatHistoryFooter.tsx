import type { JSX } from 'react'

import { InstructionForm } from '@/components/organisms/InstructionForm'

import { newInstructionControl, footerForm } from './style.css'

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
  <section className={newInstructionControl}>
    <div className={footerForm}>
      <InstructionForm
        currentSessionId={currentSessionId}
        onSendInstruction={onSendInstruction}
        isStreaming={isStreaming}
      />
    </div>
  </section>
)
