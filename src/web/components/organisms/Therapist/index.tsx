import type { JSX } from 'react'

import { Heading } from '@/components/atoms/Heading'
import { IconReload } from '@/components/atoms/IconReload'
import { Tooltip } from '@/components/organisms/Tooltip'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useTherapistActions } from './hooks/useTherapistActions'
import { useTherapistHandlers } from './hooks/useTherapistHandlers'
import * as styles from './style.css'
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
    handleDeletionChange,
    handleEditChange,
    handleApply
  } = useTherapistHandlers(actions, sessionId, onRefresh)

  return (
    <div className={styles.wrapper}>
      <div className={styles.header} role="region" aria-label="Therapist Diagnosis">
        <Heading level={4} className={styles.title}>
          Therapist Diagnosis(experimental)
        </Heading>
        {diagnosis ? (
          <Tooltip content="Re-diagnose" placement="bottom">
            <button
              type="button"
              className={styles.reloadButton}
              onClick={handleDiagnose}
              aria-label="Re-diagnose"
              disabled={isSubmitting}
            >
              <IconReload size={18} />
            </button>
          </Tooltip>
        ) : null}
      </div>
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
          handleDeletionChange={handleDeletionChange}
          handleEditChange={handleEditChange}
          handleApply={handleApply}
        />
      )}
    </div>
  )
}
