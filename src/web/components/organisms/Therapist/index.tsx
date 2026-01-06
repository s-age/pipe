import type { JSX } from 'react'

import { Heading } from '@/components/atoms/Heading'
import { IconReload } from '@/components/atoms/IconReload'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Tooltip } from '@/components/organisms/Tooltip'
import type { SessionDetail } from '@/lib/api/session/getSession'

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
  const sessionId = sessionDetail?.sessionId ?? ''
  const turnsCount = sessionDetail?.turns?.length ?? 0

  const {
    diagnosis,
    handleApply,
    handleDeletionChange,
    handleDiagnose,
    handleEditChange,
    isSubmitting,
    selectedCompressions,
    selectedDeletions,
    selectedEdits
  } = useTherapistHandlers(sessionId, onRefresh)

  return (
    <FlexColumn className={styles.wrapper}>
      <Flex
        justify="between"
        align="center"
        className={styles.header}
        role="region"
        aria-label="Therapist Diagnosis"
      >
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
      </Flex>
      {!diagnosis ? (
        <TherapistForm
          sessionId={sessionId}
          turnsCount={turnsCount}
          isSubmitting={isSubmitting}
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
    </FlexColumn>
  )
}
