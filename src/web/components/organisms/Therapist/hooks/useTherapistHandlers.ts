import { useCallback, useState } from 'react'

import type { Diagnosis } from '../types'

type TherapistHandlers = {
  diagnosis: Diagnosis | null
  error: string | null
  isSubmitting: boolean
  handleDiagnose: () => Promise<void>
  handleNewDiagnosis: () => void
  setDiagnosis: (diagnosis: Diagnosis | null) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
}

export const useTherapistHandlers = (): TherapistHandlers => {
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleDiagnose = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    setError(null)
    try {
      // TODO: Implement API call to Therapist agent
      // For now, mock response
      const mockDiagnosis: Diagnosis = {
        deletions: [5, 10],
        edits: [{ turn: 3, suggestion: 'Simplify "OK" to integrated response' }],
        compressions: [{ start: 1, end: 5, reason: 'Initial setup can be archived' }]
      }
      setDiagnosis(mockDiagnosis)
    } catch {
      setError('Diagnosis failed')
    } finally {
      setIsSubmitting(false)
    }
  }, [])

  const handleNewDiagnosis = useCallback((): void => {
    setDiagnosis(null)
  }, [])

  return {
    diagnosis,
    error,
    isSubmitting,
    handleDiagnose,
    handleNewDiagnosis,
    setDiagnosis,
    setError,
    setIsSubmitting
  }
}
