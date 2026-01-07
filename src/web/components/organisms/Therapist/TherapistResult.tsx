import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Checkbox } from '@/components/atoms/Checkbox'
import { Heading } from '@/components/atoms/Heading'
import { Label } from '@/components/atoms/Label'
import { Box } from '@/components/molecules/Box'
import { Code } from '@/components/molecules/Code'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { ListItem } from '@/components/molecules/ListItem'
import { Paragraph } from '@/components/molecules/Paragraph'
import { UnorderedList } from '@/components/molecules/UnorderedList'
// reload icon removed from initial display per design decision

import * as styles from './style.css'
import type { Diagnosis } from './types'

export type TherapistResultProperties = {
  diagnosis: Diagnosis
  isSubmitting: boolean
  selectedCompressions: { end: number; reason: string; start: number }[]
  selectedDeletions: number[]
  selectedEdits: { newContent: string; turn: number }[]
  handleApply: () => void
  handleDeletionChange: (
    turn: number
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleEditChange: (edit: {
    newContent: string
    turn: number
  }) => (event: React.ChangeEvent<HTMLInputElement>) => void
}

export const TherapistResult = ({
  diagnosis,
  isSubmitting,
  selectedCompressions,
  selectedDeletions,
  selectedEdits,
  handleApply,
  handleDeletionChange,
  handleEditChange
}: TherapistResultProperties): JSX.Element => (
  <FlexColumn className={styles.container}>
    <FlexColumn className={styles.body}>
      <Box className={styles.results}>
        <Heading level={5} className={styles.resultItemHeading}>
          Summary:
        </Heading>
        <Paragraph>
          The therapist has identified the following issues and suggestions for the
          session:
        </Paragraph>
        <Paragraph>{diagnosis.summary}</Paragraph>

        <Heading level={5} className={styles.resultItemHeading}>
          Deletions:
        </Heading>
        <UnorderedList className={styles.list}>
          {diagnosis.deletions?.map((turn: number) => (
            <ListItem key={turn}>
              <Label className={styles.checkboxLabel}>
                <Checkbox onChange={handleDeletionChange(turn)} />
                Turn {turn}: Suggested removal
              </Label>
            </ListItem>
          )) || <ListItem>None</ListItem>}
        </UnorderedList>

        <Heading level={5} className={styles.resultItemHeading}>
          Edits:
        </Heading>
        <UnorderedList className={styles.list}>
          {diagnosis.edits?.map((edit) => (
            <ListItem key={edit.turn}>
              <Label className={styles.checkboxLabel}>
                <Checkbox onChange={handleEditChange(edit)} />
                Turn {edit.turn}: {edit.newContent}
              </Label>
            </ListItem>
          )) || <ListItem>None</ListItem>}
        </UnorderedList>

        <Heading level={5} className={styles.resultItemHeading}>
          Compressions:
        </Heading>
        <UnorderedList className={styles.list}>
          {diagnosis.compressions?.map((comp) => (
            <ListItem key={`${comp.start}-${comp.end}`}>
              <Label className={styles.checkboxLabel}>
                Turns {comp.start}-{comp.end}: {comp.reason}
              </Label>
            </ListItem>
          )) || <ListItem>None</ListItem>}
        </UnorderedList>
        {diagnosis.rawDiagnosis && (
          <>
            <Heading level={5}>Raw Diagnosis:</Heading>
            <Code block={true}>{diagnosis.rawDiagnosis}</Code>
          </>
        )}
      </Box>
    </FlexColumn>
    <Box className={styles.buttonContainer}>
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
    </Box>
  </FlexColumn>
)
