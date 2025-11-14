import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useFormContext } from '@/components/organisms/Form'
import { emitToast } from '@/lib/toastEvents'

export type UseInstructionFormHandlersProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
}

export type UseInstructionFormHandlersReturn = {
  register: UseFormRegister<FieldValues>
  submit: () => Promise<void>
  onTextAreaKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onSendClick: () => void
}

export const useInstructionFormHandlers = ({
  currentSessionId,
  onSendInstruction
}: UseInstructionFormHandlersProperties): UseInstructionFormHandlersReturn => {
  const methods = useFormContext()
  const { register, handleSubmit, reset } = methods

  const submit = handleSubmit(async (data) => {
    const instruction = (data as { instruction?: string }).instruction ?? ''
    if (!instruction.trim() || !currentSessionId) return

    try {
      await onSendInstruction(instruction)
      reset({ instruction: '' })
    } catch (error) {
      emitToast.failure(
        error instanceof Error ? error.message : 'Failed to send instruction'
      )
      console.error('Failed to send instruction:', error)
    }
  })

  const onTextAreaKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void submit()
    }
  }

  const onSendClick = (): void => {
    void submit()
  }

  return { register, submit, onTextAreaKeyDown, onSendClick }
}
