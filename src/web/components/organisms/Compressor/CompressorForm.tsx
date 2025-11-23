import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputText } from '@/components/molecules/InputText'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { useCompressorActions } from './hooks/useCompressorActions'
import * as styles from './style.css'
import { renderTurnOptions } from './TurnOptions'

export type CompressorFormProperties = {
  sessionId: string
  effectiveMax: number
  isSubmitting: boolean
  execResult: string | null
  error?: string | null
  startLocal: number
  endLocal: number
  handleStartChange: (event: React.ChangeEvent<HTMLSelectElement>) => void
  handleEndChange: (event: React.ChangeEvent<HTMLSelectElement>) => void
  endOptions: number[]
  setSummary: (summary: string) => void
  setStage: (stage: 'form' | 'approval') => void
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
}

export const CompressorForm = ({
  sessionId,
  effectiveMax,
  isSubmitting,
  execResult,
  error,
  startLocal,
  endLocal,
  handleStartChange,
  handleEndChange,
  endOptions,
  setSummary,
  setStage,
  setError,
  setIsSubmitting
}: CompressorFormProperties): JSX.Element => {
  const formContext = useOptionalFormContext()

  const { handleExecute } = useCompressorActions({
    sessionId,
    setSummary,
    setStage,
    setError,
    setIsSubmitting
  })

  return (
    <>
      <input type="hidden" id="current-session-id" value={sessionId} />
      <div className={styles.form}>
        <Fieldset legend="Compression Policy" className={styles.fieldsetContainer}>
          <TextArea
            name="policy"
            rows={4}
            placeholder="Compression policy"
            register={formContext?.register}
          />
        </Fieldset>
        <Fieldset legend="Target length (tokens)" className={styles.fieldsetContainer}>
          <InputText
            name="targetLength"
            type="number"
            placeholder="1000"
            register={formContext?.register}
          />
        </Fieldset>
        <Fieldset legend="Range" className={styles.fieldsetContainer}>
          <div className={styles.field}>
            <div className={styles.label}>Start Turn</div>
            <select
              className={styles.input}
              {...(formContext?.register ? formContext.register('startTurn') : {})}
              value={String(startLocal)}
              onChange={handleStartChange}
            >
              {renderTurnOptions(effectiveMax, endLocal - 1)}
            </select>
          </div>

          <div className={styles.field}>
            <div className={styles.label}>End Turn</div>
            <select
              className={styles.input}
              {...(formContext?.register ? formContext.register('endTurn') : {})}
              value={String(endLocal)}
              onChange={handleEndChange}
            >
              {endOptions.map((turn: number) => (
                <option key={turn} value={String(turn)}>
                  {turn}
                </option>
              ))}
            </select>
          </div>
        </Fieldset>

        {error && (
          <div className={styles.errorBox}>
            <div className={styles.errorTitle}>Error</div>
            <pre className={styles.pre}>{error}</pre>
          </div>
        )}

        {execResult && (
          <div className={styles.previewBox}>
            <div className={styles.previewTitle}>Execution Result</div>
            <pre className={styles.pre}>{execResult}</pre>
          </div>
        )}
      </div>

      <div className={styles.buttonContainer}>
        <Button
          kind="primary"
          size="default"
          type="button"
          disabled={isSubmitting}
          onClick={handleExecute}
          className={styles.executeButton}
        >
          {isSubmitting ? 'Executing...' : 'Execute'}
        </Button>
      </div>
    </>
  )
}
