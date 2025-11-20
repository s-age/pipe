import React from 'react'

import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { MetaItem } from '@/components/molecules/MetaItem'
import { Slider } from '@/components/molecules/Slider'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersHandlers } from './hooks/useHyperParametersHandlers'
import { hyperparametersControl, sliderContainer, labelContainer } from './style.css'

type HyperParametersProperties = {
  sessionDetail: SessionDetail
}

export const HyperParameters = ({
  sessionDetail
}: HyperParametersProperties): React.JSX.Element => {
  const formContext = useOptionalFormContext()
  const errors = formContext?.formState?.errors
  const {
    temperature,
    setTemperature,
    handleTemperatureMouseUp,
    handleTemperatureMouseDown,
    topP,
    setTopP,
    handleTopPMouseUp,
    handleTopPMouseDown,
    topK,
    setTopK,
    handleTopKMouseUp,
    handleTopKMouseDown
  } = useHyperParametersHandlers({ sessionDetail })

  return (
    <MetaItem>
      <Fieldset
        legend="Hyperparameters"
        error={errors?.hyperparameters as unknown as React.ReactNode}
      >
        <div>
          <div className={hyperparametersControl}>
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
          </div>

          <div className={hyperparametersControl}>
            <div className={labelContainer}>
              <Label>Top P:</Label>
            </div>
            <div className={sliderContainer}>
              <Slider
                min={0}
                max={1}
                step={0.1}
                name="hyperparameters.top_p"
                value={topP}
                onChange={setTopP}
                onMouseDown={handleTopPMouseDown}
                onMouseUp={handleTopPMouseUp}
              />
            </div>
          </div>

          <div className={hyperparametersControl}>
            <div className={labelContainer}>
              <Label>Top K:</Label>
            </div>
            <div className={sliderContainer}>
              <Slider
                min={1}
                max={50}
                step={1}
                name="hyperparameters.top_k"
                value={topK}
                onChange={setTopK}
                onMouseDown={handleTopKMouseDown}
                onMouseUp={handleTopKMouseUp}
              />
            </div>
          </div>
        </div>
      </Fieldset>
    </MetaItem>
  )
}
