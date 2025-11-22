import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputText } from '@/components/molecules/InputText'
import { TextArea } from '@/components/molecules/TextArea'
import { Form, useOptionalFormContext } from '@/components/organisms/Form'
import { useSessionStore } from '@/stores/useChatHistoryStore'

import {
  useCompressorHandlers,
  type UseCompressorHandlersReturn
} from './hooks/useCompressorHandlers'
import { useCompressorLifecycle } from './hooks/useCompressorLifecycle'
import { compressorSchema } from './schema'
import * as styles from './style.css'
import { renderTurnOptions } from './TurnOptions'

export type CompressorProperties = {
  sessionId: string
  mockMaxTurn?: number
}

const CompressContent = ({
  handlers,
  isSubmitting,
  execResult,
  handleExecuteClick,
  sessionId,
  effectiveMax
}: {
  handlers: UseCompressorHandlersReturn
  isSubmitting: boolean
  execResult: string | null
  handleExecuteClick: () => Promise<void>
  sessionId: string
  effectiveMax: number
}): JSX.Element => {
  const { startLocal, endLocal, handleStartChange, handleEndChange, endOptions } =
    handlers
  const formContext = useOptionalFormContext()

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
        <Fieldset
          legend="Target length (characters)"
          className={styles.fieldsetContainer}
        >
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
              name="startTurn"
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
              name="endTurn"
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
          onClick={handleExecuteClick}
          className={styles.executeButton}
        >
          {isSubmitting ? 'Executing...' : 'Execute'}
        </Button>
      </div>
    </>
  )
}

export const Compressor = ({
  sessionId,
  mockMaxTurn
}: CompressorProperties): JSX.Element => {
  const { state } = useSessionStore()
  const { sessionDetail } = state

  const maxTurn = sessionDetail?.turns?.length ?? 0
  const effectiveMax = maxTurn > 0 ? maxTurn : (mockMaxTurn ?? 0)

  const { mergedDefaultValues } = useCompressorLifecycle({
    effectiveMax
  })

  const handlers = useCompressorHandlers({
    sessionId,
    effectiveMax
  })

  const { handleExecuteClick, isSubmitting, execResult } = handlers

  return (
    <Form defaultValues={mergedDefaultValues} schema={compressorSchema}>
      <CompressContent
        handlers={handlers}
        isSubmitting={isSubmitting}
        execResult={execResult}
        handleExecuteClick={handleExecuteClick}
        sessionId={sessionId}
        effectiveMax={effectiveMax}
      />
    </Form>
  )
}
