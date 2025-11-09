import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useFormContext } from '@/components/organisms/Form'

export type UseInstructionFormProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  refreshSessions: () => Promise<void>
  setError: (error: string | null) => void
}

export type UseInstructionFormReturn = {
  register: UseFormRegister<FieldValues>
  submit: () => Promise<void>
  // React event-friendly handlers
  onTextAreaKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onSendClick: () => void
}

export const useInstructionForm = ({
  currentSessionId,
  onSendInstruction,
  refreshSessions,
  setError,
}: UseInstructionFormProperties): UseInstructionFormReturn => {
  const methods = useFormContext()
  const { register, handleSubmit, reset } = methods

  const submit = handleSubmit(async (data) => {
    const instruction = (data as { instruction?: string }).instruction ?? ''
    if (!instruction.trim() || !currentSessionId) return

    try {
      await onSendInstruction(instruction)
      await refreshSessions()
      reset({ instruction: '' })
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to send instruction')
      // keep logging for debugging
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
