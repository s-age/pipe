import type { JSX } from 'react'

import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Flex } from '@/components/molecules/Flex'
import { MetaItem } from '@/components/molecules/MetaItem'
import { Slider } from '@/components/molecules/Slider'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersHandlers } from './hooks/useHyperParametersHandlers'
import {
  hyperparametersControl,
  sliderContainer,
  labelContainer,
  note
} from './style.css'

type HyperParametersProperties = {
  sessionDetail: SessionDetail
}

export const HyperParameters = ({
  sessionDetail
}: HyperParametersProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const errors = formContext?.formState?.errors
  const {
    handleTemperatureMouseDown,
    handleTemperatureMouseUp,
    handleTopKMouseDown,
    handleTopKMouseUp,
    handleTopPMouseDown,
    handleTopPMouseUp,
    setTemperature,
    setTopK,
    setTopP,
    temperature,
    topK,
    topP
  } = useHyperParametersHandlers({ sessionDetail })

  return (
    <MetaItem>
      <Fieldset
        legend="Hyperparameters"
        error={
          errors?.hyperparameters?.message
            ? String(errors.hyperparameters.message)
            : undefined
        }
      >
        <p className={note}>
          Hyperparameters are fixed for GeminiAPI, but left to the model&apos;s
          discretion for gemini-cli.
        </p>
        <div>
          <Flex align="center" gap="m" className={hyperparametersControl}>
            <div className={labelContainer}>
              <Label>Temperature:</Label>
            </div>
            <div className={sliderContainer}>
              <Slider
                min={0}
                max={2}
                step={0.1}
                name="hyperparameters.temperature"
                value={temperature}
                onChange={setTemperature}
                onMouseDown={handleTemperatureMouseDown}
                onMouseUp={handleTemperatureMouseUp}
                tabIndex={-1}
              />
            </div>
          </Flex>

          <Flex align="center" gap="m" className={hyperparametersControl}>
            <div className={labelContainer}>
              <Label>Top P:</Label>
            </div>
            <div className={sliderContainer}>
              <Slider
                min={0}
                max={1}
                step={0.1}
                name="hyperparameters.topP"
                value={topP}
                onChange={setTopP}
                onMouseDown={handleTopPMouseDown}
                onMouseUp={handleTopPMouseUp}
              />
            </div>
          </Flex>

          <Flex align="center" gap="m" className={hyperparametersControl}>
            <div className={labelContainer}>
              <Label>Top K:</Label>
            </div>
            <div className={sliderContainer}>
              <Slider
                min={1}
                max={50}
                step={1}
                name="hyperparameters.topK"
                value={topK}
                onChange={setTopK}
                onMouseDown={handleTopKMouseDown}
                onMouseUp={handleTopKMouseUp}
              />
            </div>
          </Flex>
        </div>
      </Fieldset>
    </MetaItem>
  )
}
