import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { CompressorApproval } from './CompressorApproval'
import { CompressorForm } from './CompressorForm'
import { useCompressorLifecycle } from './hooks/useCompressorLifecycle'
import { useCompressorStateHandlers } from './hooks/useCompressorStateHandlers'
import { compressorSchema } from './schema'

export type CompressorProperties = {
  sessionDetail: SessionDetail | null
}

export const Compressor = ({ sessionDetail }: CompressorProperties): JSX.Element => {
  const sessionId = sessionDetail?.session_id ?? ''
  const maxTurn = sessionDetail?.turns?.length ?? 0
  const effectiveMax = maxTurn

  const { mergedDefaultValues } = useCompressorLifecycle({
    effectiveMax
  })

  const {
    stage,
    summary,
    error,
    isSubmitting,
    startLocal,
    endLocal,
    handleStartChange,
    handleEndChange,
    endOptions,
    handleDeny,
    setSummary,
    setStage,
    setError,
    setIsSubmitting
  } = useCompressorStateHandlers({
    effectiveMax
  })

  return (
    <Form defaultValues={mergedDefaultValues} schema={compressorSchema}>
      {stage === 'form' ? (
        <CompressorForm
          sessionId={sessionId}
          effectiveMax={effectiveMax}
          isSubmitting={isSubmitting}
          execResult={null}
          error={error}
          startLocal={startLocal}
          endLocal={endLocal}
          handleStartChange={handleStartChange}
          handleEndChange={handleEndChange}
          endOptions={endOptions}
          setSummary={setSummary}
          setStage={setStage}
          setError={setError}
          setIsSubmitting={setIsSubmitting}
        />
      ) : (
        <CompressorApproval
          summary={summary}
          sessionId={sessionId}
          setSummary={setSummary}
          setStage={setStage}
          setError={setError}
          setIsSubmitting={setIsSubmitting}
          handleDeny={handleDeny}
          isSubmitting={isSubmitting}
        />
      )}
    </Form>
  )
}
