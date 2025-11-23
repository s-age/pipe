import { useCallback, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'

type UseCompressorStateHandlersProperties = {
  effectiveMax: number
}

export type UseCompressorStateHandlersReturn = {
  stage: 'form' | 'approval'
  summary: string
  error: string | null
  isSubmitting: boolean
  startLocal: number
  endLocal: number
  handleStartChange: (event: ChangeEvent<HTMLSelectElement>) => void
  handleEndChange: (event: ChangeEvent<HTMLSelectElement>) => void
  endOptions: number[]
  handleDeny: () => void
  setSummary: (summary: string) => void
  setStage: (stage: 'form' | 'approval') => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
}

export const useCompressorStateHandlers = ({
  effectiveMax
}: UseCompressorStateHandlersProperties): UseCompressorStateHandlersReturn => {
  const [stage, setStage] = useState<'form' | 'approval'>('form')
  const [summary, setSummary] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [startLocal, setStartLocal] = useState<number>(1)
  const [endLocal, setEndLocal] = useState<number>(effectiveMax)

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

  const handleDeny = useCallback((): void => {
    setStage('form')
    setSummary('')
    setError(null)
  }, [])

  return {
    stage,
    summary,
    error,
    isSubmitting,
    startLocal,
    endLocal,
    handleStartChange,
    handleEndChange,
    endOptions,
    handleDeny,
    setSummary,
    setStage,
    setError,
    setIsSubmitting
  }
}
