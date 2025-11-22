import { useCallback, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import { useAppStore } from '@/stores/useAppStore'

import { useCompressorActions } from './useCompressorActions'
import type { CompressorFormInputs } from '../schema'

type UseCompressorHandlersProperties = {
  sessionId: string
  effectiveMax: number
}

export type UseCompressorHandlersReturn = {
  startLocal: number
  endLocal: number
  handleStartChange: (event: ChangeEvent<HTMLSelectElement>) => void
  handleEndChange: (event: ChangeEvent<HTMLSelectElement>) => void
  endOptions: number[]
  handleExecuteClick: () => Promise<void>
  isSubmitting: boolean
  execResult: string | null
}

export const useCompressorHandlers = ({
  sessionId,
  effectiveMax
}: UseCompressorHandlersProperties): UseCompressorHandlersReturn => {
  const [startLocal, setStartLocal] = useState<number>(1)
  const [endLocal, setEndLocal] = useState<number>(effectiveMax)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [execResult, setExecResult] = useState<string | null>(null)

  const { pushToast } = useAppStore()
  const { submitCompression } = useCompressorActions({ sessionId })
  const formContext = useOptionalFormContext()

  const handleStartChange = useCallback(
    (startEvent: ChangeEvent<HTMLSelectElement>): void => {
      const parsedValue = Number(startEvent.target.value)
      const newStart = Number.isNaN(parsedValue) ? 1 : parsedValue
      setStartLocal(newStart)
      // Adjust end if necessary
      const minEnd = newStart + 1
      if (endLocal < minEnd) {
        setEndLocal(minEnd)
      }
    },
    [endLocal]
  )

  const handleEndChange = useCallback(
    (endEvent: ChangeEvent<HTMLSelectElement>): void => {
      const parsedValue = Number(endEvent.target.value)
      const newEnd = Number.isNaN(parsedValue) ? effectiveMax : parsedValue
      setEndLocal(newEnd)
      // Adjust start if necessary
      if (startLocal >= newEnd) {
        setStartLocal(newEnd - 1)
      }
    },
    [startLocal, effectiveMax]
  )

  const endOptions = useMemo(() => {
    const minEnd = startLocal + 1
    const maxEnd = effectiveMax

    return Array.from(
      { length: Math.max(0, maxEnd - minEnd + 1) },
      (_, i) => minEnd + i
    )
  }, [startLocal, effectiveMax])

  const onSubmit = useCallback(
    async (data: CompressorFormInputs): Promise<void> => {
      setIsSubmitting(true)
      try {
        const result = await submitCompression(data)
        setExecResult(JSON.stringify(result, null, 2))
      } catch (error: unknown) {
        pushToast({
          status: 'failure',
          title: 'Compression Error',
          description: String(error)
        })
      } finally {
        setIsSubmitting(false)
      }
    },
    [submitCompression, pushToast]
  )

  const handleExecuteClick = useCallback(async (): Promise<void> => {
    await formContext?.handleSubmit(onSubmit as never)()
  }, [formContext, onSubmit])

  return {
    startLocal,
    endLocal,
    handleStartChange,
    handleEndChange,
    endOptions,
    handleExecuteClick,
    isSubmitting,
    execResult
  }
}
