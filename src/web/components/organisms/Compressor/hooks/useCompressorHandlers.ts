import { useCallback, useState } from 'react'
import type { ChangeEvent } from 'react'

type useCompressorHandlersProperties = {
  effectiveMax: number
}

export type useCompressorHandlersReturn = {
  summary: string
  error: string | null
  isSubmitting: boolean
  startLocal: number
  endLocal: number
  compressorSessionId: string | null
  handleStartChange: (event: ChangeEvent<HTMLSelectElement>) => void
  handleEndChange: (event: ChangeEvent<HTMLSelectElement>) => void
  handleDeny: () => void
  setSummary: (summary: string) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  setCompressorSessionId: (id: string | null) => void
}

export const useCompressorHandlers = ({
  effectiveMax
}: useCompressorHandlersProperties): useCompressorHandlersReturn => {
  const [summary, setSummary] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [startLocal, setStartLocal] = useState<number>(1)
  const [endLocal, setEndLocal] = useState<number>(effectiveMax)
  const [compressorSessionId, setCompressorSessionId] = useState<string | null>(null)

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

  const handleDeny = useCallback((): void => {
    setSummary('')
    setError(null)
    setCompressorSessionId(null)
  }, [])

  return {
    summary,
    error,
    isSubmitting,
    startLocal,
    endLocal,
    compressorSessionId,
    handleStartChange,
    handleEndChange,
    handleDeny,
    setSummary,
    setError,
    setIsSubmitting,
    setCompressorSessionId
  }
}
