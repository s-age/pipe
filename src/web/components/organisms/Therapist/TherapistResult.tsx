import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import * as styles from './style.css'
import type { Diagnosis } from './types'

export type TherapistResultProperties = {
  diagnosis: Diagnosis
  isSubmitting: boolean
  handleNewDiagnosis: () => void
}

export const TherapistResult = ({
  diagnosis,
  isSubmitting,
  handleNewDiagnosis
}: TherapistResultProperties): JSX.Element => (
  <div className={styles.container}>
    <div className={styles.body}>
      <h4 className={styles.title}>Diagnosis Results</h4>
      <div className={styles.results}>
        <h5>Deletions:</h5>
        <ul>
          {diagnosis.deletions?.map((turn: number) => (
            <li key={turn}>Turn {turn}: Suggested removal</li>
          )) || <li>None</li>}
        </ul>
        <h5>Edits:</h5>
        <ul>
          {diagnosis.edits?.map((edit) => (
            <li key={edit.turn}>
              Turn {edit.turn}: {edit.suggestion}
            </li>
          )) || <li>None</li>}
        </ul>
        <h5>Compressions:</h5>
        <ul>
          {diagnosis.compressions?.map((comp) => (
            <li key={`${comp.start}-${comp.end}`}>
              Turns {comp.start}-{comp.end}: {comp.reason}
            </li>
          )) || <li>None</li>}
        </ul>
      </div>
    </div>
    <div className={styles.buttonContainer}>
      <Button
        type="button"
        onClick={handleNewDiagnosis}
        disabled={isSubmitting}
        className={styles.button}
      >
        New Diagnosis
      </Button>
    </div>
  </div>
)
