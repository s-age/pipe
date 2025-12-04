import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Checkbox } from '@/components/atoms/Checkbox'
import { Heading } from '@/components/atoms/Heading'
// reload icon removed from initial display per design decision

import * as styles from './style.css'
import type { Diagnosis } from './types'

export type TherapistResultProperties = {
  diagnosis: Diagnosis
  isSubmitting: boolean
  selectedDeletions: number[]
  selectedEdits: { turn: number; new_content: string }[]
  selectedCompressions: { start: number; end: number; reason: string }[]
  handleDeletionChange: (
    turn: number
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleEditChange: (edit: {
    turn: number
    new_content: string
  }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleApply: () => void
}

export const TherapistResult = ({
  diagnosis,
  isSubmitting,
  selectedDeletions,
  selectedEdits,
  selectedCompressions,
  handleDeletionChange,
  handleEditChange,
  handleApply
}: TherapistResultProperties): JSX.Element => (
  <div className={styles.container}>
    <div className={styles.body}>
      <div className={styles.results}>
        <Heading level={5} className={styles.resultItemHeading}>
          Summary:
        </Heading>
        <p>
          The therapist has identified the following issues and suggestions for the
          session:
        </p>
        <p>{diagnosis.summary}</p>

        <Heading level={5} className={styles.resultItemHeading}>
          Deletions:
        </Heading>
        <ul className={styles.list}>
          {diagnosis.deletions?.map((turn: number) => (
            <li key={turn}>
              <label>
                <Checkbox onChange={handleDeletionChange(turn)} />
                Turn {turn}: Suggested removal
              </label>
            </li>
          )) || <li>None</li>}
        </ul>

        <Heading level={5} className={styles.resultItemHeading}>
          Edits:
        </Heading>
        <ul className={styles.list}>
          {diagnosis.edits?.map((edit) => (
            <li key={edit.turn}>
              <label>
                <Checkbox onChange={handleEditChange(edit)} />
                Turn {edit.turn}: {edit.new_content}
              </label>
            </li>
          )) || <li>None</li>}
        </ul>

        <Heading level={5} className={styles.resultItemHeading}>
          Compressions:
        </Heading>
        <ul className={styles.list}>
          {diagnosis.compressions?.map((comp) => (
            <li key={`${comp.start}-${comp.end}`}>
              <label>
                Turns {comp.start}-{comp.end}: {comp.reason}
              </label>
            </li>
          )) || <li>None</li>}
        </ul>
        {diagnosis.raw_diagnosis && (
          <>
            <Heading level={5}>Raw Diagnosis:</Heading>
            <pre>{diagnosis.raw_diagnosis}</pre>
          </>
        )}
      </div>
    </div>
    <div className={styles.buttonContainer}>
      <Button
        type="button"
        onClick={handleApply}
        disabled={
          isSubmitting ||
          (selectedDeletions.length === 0 &&
            selectedEdits.length === 0 &&
            selectedCompressions.length === 0)
        }
        className={styles.button}
      >
        Apply Selected Modifications
      </Button>
    </div>
  </div>
)
