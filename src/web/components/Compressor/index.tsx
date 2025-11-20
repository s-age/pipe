import type { JSX } from 'react'
import React, { useCallback, useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { InputText } from '@/components/molecules/InputText'
import { TextArea } from '@/components/molecules/TextArea'
import { Form, useOptionalFormContext } from '@/components/organisms/Form'

import { renderTurnOptions } from './helpers'
import { useCompressorHandlers } from './hooks/useCompressorHandlers'
import { compressorSchema } from './schema'
import * as styles from './style.css'

type Tab = 'Meta' | 'Compress' | 'Therapist'
export type CompressorProperties = {
  sessionId: string
  mockMaxTurn?: number
  showTabs?: boolean
}

export const Compressor = ({
  sessionId,
  mockMaxTurn,
  showTabs = true
}: CompressorProperties): JSX.Element => {
  const [active, setActive] = useState<Tab>('Compress')
  const [maxTurn, setMaxTurn] = useState<number>(0)

  const { defaultValues, onSubmit, isSubmitting, execResult } = useCompressorHandlers({
    sessionId
  })

  const effectiveMax = maxTurn > 0 ? maxTurn : (mockMaxTurn ?? 0)

  // Ensure the form's defaultValues set `endTurn` to the current maximum when
  // no endTurn is provided by the handler. This initializes End to Max.
  const mergedDefaultValues = useMemo(() => {
    try {
      const dv = { ...(defaultValues as Record<string, unknown>) }
      if ((dv.endTurn === undefined || dv.endTurn === null) && effectiveMax > 0) {
        ;(dv as Record<string, number>).endTurn = effectiveMax
      }

      return dv as typeof defaultValues
    } catch {
      return defaultValues
    }
  }, [defaultValues, effectiveMax])

  const CompressContent = (): JSX.Element => {
    const formContext = useOptionalFormContext()

    // Local state for start/end to avoid using `watch`. Keep values in local
    // state and sync to react-hook-form via `setValue`.
    const [startLocal, setStartLocal] = React.useState<number | undefined>(
      () => (mergedDefaultValues?.startTurn as number | undefined) ?? undefined
    )
    const [endLocal, setEndLocal] = React.useState<number>(
      () => (mergedDefaultValues?.endTurn as number | undefined) ?? effectiveMax
    )

    // Sync locals to form when they change
    React.useEffect(() => {
      if (typeof startLocal === 'number') {
        formContext?.setValue('startTurn', startLocal)
      } else {
        formContext?.setValue('startTurn', undefined)
      }
      formContext?.setValue('endTurn', endLocal)
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [startLocal, endLocal])

    // When merged defaults or effectiveMax change, ensure locals reflect them
    React.useEffect(() => {
      // initialize or adjust endLocal to effectiveMax if not set
      const mdStart = mergedDefaultValues?.startTurn as number | undefined
      const mdEnd = mergedDefaultValues?.endTurn as number | undefined
      if (typeof mdStart === 'number') setStartLocal(mdStart)
      if (typeof mdEnd === 'number') setEndLocal(mdEnd)
      if ((mdEnd === undefined || mdEnd === null) && effectiveMax > 0) {
        setEndLocal(effectiveMax)
      }
      // ensure endLocal doesn't exceed effectiveMax
      if (endLocal > effectiveMax) setEndLocal(effectiveMax)
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [mergedDefaultValues, effectiveMax])

    const handleExecuteClick = React.useCallback((): void => {
      void formContext?.handleSubmit(onSubmit as never)()
    }, [formContext])

    const handleStartChange = React.useCallback(
      (startEvent: React.ChangeEvent<HTMLSelectElement>): void => {
        const parsedValue = Number(startEvent.target.value)
        const newStart = Number.isNaN(parsedValue) ? undefined : parsedValue
        // If newStart exceeds current end, move end up to newStart
        if (typeof newStart === 'number' && newStart > endLocal) {
          setEndLocal(newStart)
        }
        setStartLocal(newStart)
      },
      [endLocal]
    )

    const handleEndChange = React.useCallback(
      (endEvent: React.ChangeEvent<HTMLSelectElement>): void => {
        const parsedValue = Number(endEvent.target.value)
        const newEnd = Number.isNaN(parsedValue) ? effectiveMax : parsedValue
        // If newEnd is below start, pull start down
        if (startLocal === undefined || newEnd < startLocal) {
          setStartLocal(newEnd)
        }
        setEndLocal(newEnd)
      },
      [startLocal]
    )

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
                value={startLocal ?? ''}
                onChange={handleStartChange}
              >
                {renderTurnOptions(effectiveMax, undefined)}
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
                {Array.from(
                  { length: effectiveMax },
                  (_ignored, index) => index + 1
                ).map((turn) => (
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
  const handleTabClick = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>): void => {
      const tab = event.currentTarget.dataset.tab as Tab | undefined
      if (tab) setActive(tab)
    },
    []
  )

  useEffect(() => {
    let mounted = true
    const loadTurns = async (): Promise<void> => {
      if (!sessionId) {
        if (mounted) setMaxTurn(0)

        return
      }
      try {
        const response = await fetch(
          `/api/sessions/${encodeURIComponent(sessionId)}/turns`
        )
        if (!response.ok) {
          if (mounted) setMaxTurn(0)

          return
        }
        const data = await response.json()

        const mt = Array.isArray(data.turns)
          ? data.turns.length
          : typeof data.maxTurn === 'number'
            ? data.maxTurn
            : 0
        if (mounted) setMaxTurn(mt)
      } catch {
        if (mounted) setMaxTurn(0)
      }
    }
    void loadTurns()

    return (): void => {
      mounted = false
    }
  }, [sessionId])

  return (
    <div className={styles.container}>
      {showTabs && (
        <div className={styles.tabHeader}>
          <button
            data-tab="Meta"
            className={active === 'Meta' ? styles.tabButtonActive : styles.tabButton}
            onClick={handleTabClick}
          >
            Meta
          </button>
          <button
            data-tab="Compress"
            className={
              active === 'Compress' ? styles.tabButtonActive : styles.tabButton
            }
            onClick={handleTabClick}
          >
            Compress
          </button>
          <button
            data-tab="Therapist"
            className={
              active === 'Therapist' ? styles.tabButtonActive : styles.tabButton
            }
            onClick={handleTabClick}
          >
            Therapist
          </button>
        </div>
      )}

      <div className={styles.tabBody}>
        {active === 'Meta' && (
          <div>
            <h4 className={styles.sectionTitle}>Session Meta</h4>
            <p className={styles.muted}>
              Session metadata will appear here (placeholder).
            </p>
          </div>
        )}

        {active === 'Compress' && (
          <Form defaultValues={mergedDefaultValues} schema={compressorSchema}>
            <CompressContent />
          </Form>
        )}

        {active === 'Therapist' && (
          <div>
            <h4 className={styles.sectionTitle}>Therapist (coming soon)</h4>
            <p className={styles.muted}>Therapist agent will be added later.</p>
          </div>
        )}
      </div>
    </div>
  )
}
