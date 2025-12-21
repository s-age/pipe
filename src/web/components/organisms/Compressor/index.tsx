import type { JSX } from 'react'

import { Form, useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { CompressorApproval } from './CompressorApproval'
import { CompressorForm } from './CompressorForm'
import { useCompressorHandlers } from './hooks/useCompressorHandlers'
import { useCompressorLifecycle } from './hooks/useCompressorLifecycle'
import { compressorSchema, type CompressorFormInputs } from './schema'

export type CompressorProperties = {
  sessionDetail: SessionDetail | null
  onRefresh: () => Promise<void>
}

const CompressorContent = ({
  sessionDetail,
  onRefresh
}: CompressorProperties): JSX.Element => {
  const sessionId = sessionDetail?.sessionId ?? ''
  const maxTurn = sessionDetail?.turns?.length ?? 0
  const effectiveMax = maxTurn

  const {
    summary,
    error,
    isSubmitting,
    startLocal,
    endLocal,
    compressorSessionId,
    handleStartChange,
    handleEndChange,
    handleDeny,
    setSummary,
    setError,
    setIsSubmitting,
    setCompressorSessionId
  } = useCompressorHandlers({
    effectiveMax
  })

  const formContext = useOptionalFormContext<CompressorFormInputs>()

  const { endOptions } = useCompressorLifecycle({
    effectiveMax,
    startLocal,
    endLocal,
    formContext
  })

  return (
    <>
      {!compressorSessionId || !summary || summary.startsWith('Rejected:') ? (
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
          setError={setError}
          setIsSubmitting={setIsSubmitting}
          compressorSessionId={compressorSessionId}
          setCompressorSessionId={setCompressorSessionId}
          onRefresh={onRefresh}
        />
      ) : (
        <CompressorApproval
          summary={summary}
          sessionId={sessionId}
          setSummary={setSummary}
          setError={setError}
          setIsSubmitting={setIsSubmitting}
          handleDeny={handleDeny}
          isSubmitting={isSubmitting}
          start={startLocal}
          end={endLocal}
          compressorSessionId={compressorSessionId}
          setCompressorSessionId={setCompressorSessionId}
          onRefresh={onRefresh}
        />
      )}
    </>
  )
}

export const Compressor = ({
  sessionDetail,
  onRefresh
}: CompressorProperties): JSX.Element => {
  const maxTurn = sessionDetail?.turns?.length ?? 0
  const effectiveMax = maxTurn

  const { mergedDefaultValues } = useCompressorLifecycle({
    effectiveMax,
    startLocal: 1,
    endLocal: effectiveMax,
    formContext: undefined
  })

  return (
    <Form defaultValues={mergedDefaultValues} schema={compressorSchema}>
      <CompressorContent sessionDetail={sessionDetail} onRefresh={onRefresh} />
    </Form>
  )
}
