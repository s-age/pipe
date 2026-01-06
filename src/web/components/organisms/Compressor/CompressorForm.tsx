import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { InputText } from '@/components/molecules/InputText'
import { ScrollArea } from '@/components/molecules/ScrollArea'
import { TextArea } from '@/components/molecules/TextArea'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { useCompressorFormLogic } from './hooks/useCompressorFormLogic'
import type { CompressorFormInputs } from './schema'
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
  setError: (error: string | null) => void
  setIsSubmitting: (isSubmitting: boolean) => void
  compressorSessionId: string | null
  setCompressorSessionId: (id: string | null) => void
  onRefresh: () => Promise<void>
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
  setError,
  setIsSubmitting,
  compressorSessionId,
  setCompressorSessionId,
  onRefresh
}: CompressorFormProperties): JSX.Element => {
  const formContext = useOptionalFormContext<CompressorFormInputs>()

  const { onExecuteClick } = useCompressorFormLogic({
    sessionId,
    setSummary,
    setError,
    setIsSubmitting,
    compressorSessionId,
    setCompressorSessionId,
    onRefresh
  })

  return (
    <>
      <input type="hidden" id="current-session-id" value={sessionId} />
      <FlexColumn gap="s" className={styles.form}>
        <ScrollArea>
          <Box padding="m" radius="m" className={styles.previewBox}>
            <Fieldset legend="Compression Policy" className={styles.fieldsetContainer}>
              <TextArea name="policy" rows={4} placeholder="Compression policy" />
            </Fieldset>
            <Fieldset
              legend="Target length (tokens)"
              className={styles.fieldsetContainer}
            >
              <InputText name="targetLength" type="number" placeholder="1000" />
            </Fieldset>
            <Fieldset legend="Range" className={styles.fieldsetContainer}>
              <FlexColumn>
                <Text size="xs" className={styles.label}>
                  Start Turn
                </Text>
                <select
                  className={styles.input}
                  {...(formContext?.register ? formContext.register('startTurn') : {})}
                  value={String(startLocal)}
                  onChange={handleStartChange}
                >
                  {renderTurnOptions(effectiveMax, endLocal - 1)}
                </select>
              </FlexColumn>

              <FlexColumn>
                <Text size="xs" className={styles.label}>
                  End Turn
                </Text>
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
              </FlexColumn>
            </Fieldset>

            {error && (
              <Box padding="s" radius="m" className={styles.errorBox}>
                <Text size="xs" weight="semibold" className={styles.errorTitle}>
                  Error
                </Text>
                <pre className={styles.pre}>{error}</pre>
              </Box>
            )}

            {execResult && (
              <Box padding="m" radius="m" className={styles.previewBox}>
                <Text size="xs" weight="semibold" className={styles.previewTitle}>
                  Execution Result
                </Text>
                <pre className={styles.pre}>{execResult}</pre>
              </Box>
            )}
          </Box>
        </ScrollArea>

        <Flex gap="s" className={styles.buttonContainer}>
          <Button
            kind="primary"
            size="default"
            type="button"
            disabled={isSubmitting}
            onClick={onExecuteClick}
            className={styles.executeButton}
          >
            {isSubmitting ? 'Compressing...' : 'Compress'}
          </Button>
        </Flex>
      </FlexColumn>
    </>
  )
}
