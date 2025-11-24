import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import { useCompressorActions } from './hooks/useCompressorActions'
import * as styles from './style.css'

export type CompressorApprovalProperties = {
  summary: string
  sessionId: string
  start?: number
  end?: number
  setSummary: (summary: string) => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  handleDeny: () => void
  isSubmitting?: boolean
  compressorSessionId: string | null
  setCompressorSessionId: (id: string | null) => void
  onRefresh: () => Promise<void>
}

export const CompressorApproval = ({
  summary,
  sessionId,
  start,
  end,
  setSummary,
  setError,
  setIsSubmitting,
  handleDeny,
  isSubmitting = false,
  compressorSessionId,
  setCompressorSessionId,
  onRefresh
}: CompressorApprovalProperties): JSX.Element => {
  const { handleApprove } = useCompressorActions({
    sessionId,
    setSummary,
    setError,
    setIsSubmitting,
    compressorSessionId,
    setCompressorSessionId,
    onRefresh
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
