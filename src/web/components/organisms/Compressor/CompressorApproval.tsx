import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import { useCompressorApprovalHandlers } from './hooks/useCompressorApprovalHandlers'
import * as styles from './style.css'

export type CompressorApprovalProperties = {
  compressorSessionId: string | null
  sessionId: string
  summary: string
  end?: number
  isSubmitting?: boolean
  start?: number
  handleDeny: () => void
  onRefresh: () => Promise<void>
  setCompressorSessionId: (id: string | null) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  setSummary: (summary: string) => void
}

export const CompressorApproval = ({
  compressorSessionId,
  summary,
  end,
  isSubmitting = false,
  start,
  handleDeny,
  onRefresh,
  setCompressorSessionId,
  setIsSubmitting,
  setSummary
}: CompressorApprovalProperties): JSX.Element => {
  const { handleApprove } = useCompressorApprovalHandlers({
    compressorSessionId,
    onRefresh,
    setSummary,
    setCompressorSessionId,
    setIsSubmitting
  })

  return (
    <div className={styles.form}>
      <div className={styles.previewBox}>
        <div className={styles.previewTitle}>
          Proposed Compression — Turns {start ?? '?'}–{end ?? '?'}
        </div>

        <div className={styles.muted}>
          The verifier sub-agent has reviewed the proposed compression and returned an
          approved result.
        </div>
        <div className={styles.muted}>
          Please review the verified summary below and confirm whether you want to
          replace turns {start ?? 'N'} through {end ?? 'N'} with this summary.
        </div>

        <div className={styles.previewTitle}>Verified summary:</div>
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
            Reject
          </Button>
          <Button
            kind="primary"
            size="default"
            type="button"
            className={styles.executeButton}
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
