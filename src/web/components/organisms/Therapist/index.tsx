import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useTherapistHandlers } from './hooks/useTherapistHandlers'
import { TherapistForm } from './TherapistForm'
import { TherapistResult } from './TherapistResult'

export type TherapistProperties = {
  sessionDetail: SessionDetail | null
  onRefresh: () => Promise<void>
}

export const Therapist = ({
  sessionDetail,
  onRefresh
}: TherapistProperties): JSX.Element => {
  const sessionId = sessionDetail?.session_id ?? ''
  const turnsCount = sessionDetail?.turns?.length ?? 0

  const {
    diagnosis,
    error,
    isSubmitting,
    handleDiagnose,
    handleNewDiagnosis,
    setDiagnosis,
    setError,
    setIsSubmitting
  } = useTherapistHandlers()

  return (
    <>
      {!diagnosis ? (
        <TherapistForm
          sessionId={sessionId}
          turnsCount={turnsCount}
          isSubmitting={isSubmitting}
          error={error}
          handleDiagnose={handleDiagnose}
          setDiagnosis={setDiagnosis}
          setError={setError}
          setIsSubmitting={setIsSubmitting}
          onRefresh={onRefresh}
        />
      ) : (
        <TherapistResult
          diagnosis={diagnosis}
          isSubmitting={isSubmitting}
          handleNewDiagnosis={handleNewDiagnosis}
        />
      )}
    </>
  )
}
