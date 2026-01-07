import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Box } from '@/components/molecules/Box'
import { Code } from '@/components/molecules/Code'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'

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
    <FlexColumn className={styles.form}>
      <Box className={styles.previewBox}>
        <Box className={styles.previewTitle}>
          Proposed Compression — Turns {start ?? '?'}–{end ?? '?'}
        </Box>

        <Box className={styles.muted}>
          The verifier sub-agent has reviewed the proposed compression and returned an
          approved result.
        </Box>
        <Box className={styles.muted}>
          Please review the verified summary below and confirm whether you want to
          replace turns {start ?? 'N'} through {end ?? 'N'} with this summary.
        </Box>

        <Box className={styles.previewTitle}>Verified summary:</Box>
        <Code block={true} className={styles.pre}>
          {summary}
        </Code>
      </Box>

      <Box className={styles.buttonContainer}>
        <Flex gap="s" className={styles.buttonRow}>
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
        </Flex>
      </Box>
    </FlexColumn>
  )
}
