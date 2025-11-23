import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import { useCompressorActions } from './hooks/useCompressorActions'
import * as styles from './style.css'

export type CompressorApprovalProperties = {
  summary: string
  sessionId: string
  setSummary: (summary: string) => void
  setStage: (stage: 'form' | 'approval') => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  handleDeny: () => void
  isSubmitting?: boolean
}

export const CompressorApproval = ({
  summary,
  sessionId,
  setSummary,
  setStage,
  setError,
  setIsSubmitting,
  handleDeny,
  isSubmitting = false
}: CompressorApprovalProperties): JSX.Element => {
  const { handleApprove } = useCompressorActions({
    sessionId,
    setSummary,
    setStage,
    setError,
    setIsSubmitting
  })

  return (
    <div className={styles.form}>
      <div className={styles.previewBox}>
        <div className={styles.previewTitle}>Summary for Approval</div>
        <pre className={styles.pre}>{summary}</pre>
      </div>

      <div className={styles.buttonContainer}>
        <div className={styles.buttonRow}>
          <Button
            kind="secondary"
            size="default"
            type="button"
            disabled={isSubmitting}
            onClick={handleDeny}
          >
            Deny
          </Button>
          <Button
            kind="primary"
            size="default"
            type="button"
            disabled={isSubmitting}
            onClick={handleApprove}
          >
            Approve
          </Button>
        </div>
      </div>
    </div>
  )
}
