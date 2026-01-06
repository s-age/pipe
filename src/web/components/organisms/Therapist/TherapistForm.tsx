import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import * as styles from './style.css'

export type TherapistFormProperties = {
  isSubmitting: boolean
  sessionId: string
  turnsCount: number
  handleDiagnose: () => Promise<void>
  onRefresh: () => Promise<void>
}

export const TherapistForm = ({
  isSubmitting,
  sessionId,
  turnsCount,
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
