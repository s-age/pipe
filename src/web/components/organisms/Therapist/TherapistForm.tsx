import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { ErrorMessage } from '@/components/atoms/ErrorMessage'

import * as styles from './style.css'

export type TherapistFormProperties = {
  sessionId: string
  turnsCount: number
  isSubmitting: boolean
  error: string | null
  handleDiagnose: () => Promise<void>
  onRefresh: () => Promise<void>
}

export const TherapistForm = ({
  sessionId,
  turnsCount,
  isSubmitting,
  error,
  handleDiagnose
}: TherapistFormProperties): JSX.Element => (
  <div className={styles.container}>
    <div className={styles.body}>
      <p className={styles.muted}>
        Session: {sessionId.substring(0, 8)}... ({turnsCount} turns)
      </p>
      <p className={styles.description}>
        Analyze session for issues: verbosity, irrelevance, redundancy. Suggest
        edits/deletions/compressions.
      </p>
      {error && <ErrorMessage message={error} />}
    </div>
    <div className={styles.buttonContainer}>
      <Button
        type="button"
        onClick={handleDiagnose}
        disabled={isSubmitting || !sessionId}
        className={styles.button}
      >
        {isSubmitting ? 'Diagnosing...' : 'Start Diagnosis'}
      </Button>
    </div>
  </div>
)
