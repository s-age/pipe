import { useCallback } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useFormContext } from '@/components/organisms/Form'
import { stopSession } from '@/lib/api/session/stopSession'
import { addToast } from '@/stores/useToastStore'

export type UseInstructionFormHandlersProperties = {
  currentSessionId: string | null
  onSendInstruction: (instruction: string) => Promise<void>
  onRefresh?: () => Promise<void>
}

export type UseInstructionFormHandlersReturn = {
  register: UseFormRegister<FieldValues>
  submit: () => Promise<void>
  onTextAreaKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void
  onStopClick: () => Promise<void>
}

export const useInstructionFormHandlers = ({
  currentSessionId,
  onSendInstruction,
  onRefresh
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

  const onStopClick = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return

    try {
      await stopSession(currentSessionId)
      addToast({
        status: 'success',
        title: 'Session stopped'
      })

      // Refresh the turns after stopping
      if (onRefresh) {
        await onRefresh()
      }
    } catch (error) {
      addToast({
        status: 'failure',
        title: 'Failed to stop session',
        description: error instanceof Error ? error.message : undefined
      })
    }
  }, [currentSessionId, onRefresh])

  return { register, submit, onTextAreaKeyDown, onStopClick }
}
