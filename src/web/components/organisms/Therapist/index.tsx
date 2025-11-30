import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useTherapistActions } from './hooks/useTherapistActions'
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

  const actions = useTherapistActions()
  const {
    diagnosis,
    error,
    isSubmitting,
    selectedDeletions,
    selectedEdits,
    selectedCompressions,
    handleDiagnose,
    handleNewDiagnosis,
    handleDeletionChange,
    handleEditChange,
    handleApply
  } = useTherapistHandlers(actions, sessionId, onRefresh)

  return (
    <>
      {!diagnosis ? (
        <TherapistForm
          sessionId={sessionId}
          turnsCount={turnsCount}
          isSubmitting={isSubmitting}
          error={error}
          handleDiagnose={handleDiagnose}
          onRefresh={onRefresh}
        />
      ) : (
        <TherapistResult
          diagnosis={diagnosis}
          isSubmitting={isSubmitting}
          selectedDeletions={selectedDeletions}
          selectedEdits={selectedEdits}
          selectedCompressions={selectedCompressions}
          handleNewDiagnosis={handleNewDiagnosis}
          handleDeletionChange={handleDeletionChange}
          handleEditChange={handleEditChange}
          handleApply={handleApply}
        />
      )}
    </>
  )
}
