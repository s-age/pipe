import React from 'react'

import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Slider } from '@/components/molecules/Slider'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersHandlers } from './hooks/useHyperParametersHandlers'
import {
  metaItem,
  hyperparametersControl,
  sliderContainer,
  labelContainer
} from './style.css'

type HyperParametersProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
}

export const HyperParameters = ({
  sessionDetail,
  currentSessionId
}: HyperParametersProperties): React.JSX.Element => {
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
  } = useHyperParametersHandlers({
    sessionDetail,
    currentSessionId
  })

  return (
    <div className={metaItem}>
      <Fieldset legend="Hyperparameters">
        {() => (
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
                  defaultValue={topP}
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
                  defaultValue={topK}
                  onChange={setTopK}
                  onMouseDown={handleTopKMouseDown}
                  onMouseUp={handleTopKMouseUp}
                />
              </div>
            </div>
          </div>
        )}
      </Fieldset>
    </div>
  )
}
