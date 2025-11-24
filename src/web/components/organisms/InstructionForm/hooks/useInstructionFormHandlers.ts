import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useFormContext } from '@/components/organisms/Form'

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

  const submit = handleSubmit(async (data: { instruction?: string }) => {
    const instruction = (data as { instruction?: string }).instruction ?? ''
    if (!instruction.trim() || !currentSessionId) return

    await onSendInstruction(instruction)
    reset({ instruction: '' })
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
