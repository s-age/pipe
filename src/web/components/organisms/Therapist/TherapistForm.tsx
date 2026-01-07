import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Box } from '@/components/molecules/Box'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Paragraph } from '@/components/molecules/Paragraph'

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
  <FlexColumn className={styles.container}>
    <FlexColumn className={styles.body}>
      <Paragraph className={styles.muted}>
        Session: {sessionId.substring(0, 8)}... ({turnsCount} turns)
      </Paragraph>
      <Paragraph className={styles.description}>
        Analyze session for issues: verbosity, irrelevance, redundancy. Suggest
        edits/deletions/compressions.
      </Paragraph>
    </FlexColumn>
    <Box className={styles.buttonContainer}>
      <Button
        type="button"
        onClick={handleDiagnose}
        disabled={isSubmitting || !sessionId}
        className={styles.button}
      >
        {isSubmitting ? 'Diagnosing...' : 'Start Diagnosis'}
      </Button>
    </Box>
  </FlexColumn>
)
