import { useCallback } from 'react'
import type { FieldValues, UseFormRegister } from 'react-hook-form'

import { useFormContext } from '@/components/organisms/Form'

import { useInstructionFormActions } from './useInstructionFormActions'

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
  const { stopSession } = useInstructionFormActions()
  const methods = useFormContext()
  const { register, handleSubmit, reset } = methods

  const submit = useCallback(async () => {
    await handleSubmit(async (data: { instruction?: string }) => {
      const instruction = data.instruction ?? ''
      if (!instruction.trim() || !currentSessionId) return

      await onSendInstruction(instruction)
      reset({ instruction: '' })
    })()
  }, [currentSessionId, onSendInstruction, handleSubmit, reset])

  const onTextAreaKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>): void => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        void submit()
      }
    },
    [submit]
  )

  const onStopClick = useCallback(async (): Promise<void> => {
    if (!currentSessionId) return

    await stopSession(currentSessionId)

    if (onRefresh) {
      await onRefresh()
    }
  }, [currentSessionId, stopSession, onRefresh])

  return { register, submit, onTextAreaKeyDown, onStopClick }
}
