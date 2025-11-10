import React from 'react'

import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Slider } from '@/components/molecules/Slider'
import { useSessionMetaSaver } from '@/components/organisms/SessionMeta/useSessionMetaSaver'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useHyperParametersHandlers } from './hooks/useHyperParametersHandlers'
import { metaItem, hyperparametersControl, sliderContainer } from './style.css'

type HyperParametersProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onRefresh: () => Promise<void>
}

export const HyperParameters = ({
  sessionDetail,
  currentSessionId,
  onRefresh
}: HyperParametersProperties): React.JSX.Element => {
  useSessionMetaSaver({ onRefresh })

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
    currentSessionId,
    // Return the onRefresh promise so the handlers can await the canonical
    // refresh and keep `isInteracting` true until the server state is
    // reflected. This prevents an intermediate overwrite from the stale
    // `sessionDetail` while a background refresh is in-flight.
    onMetaSave: (_id, _meta) => onRefresh()
  })

  return (
    <div className={metaItem}>
      <Fieldset legend="Hyperparameters">
        {() => (
          <div>
            <div className={hyperparametersControl}>
              <Label>Temperature:</Label>
              <div className={sliderContainer}>
                <Slider
                  min={0}
                  max={2}
                  step={0.1}
                  value={temperature}
                  onChange={setTemperature}
                  onMouseDown={handleTemperatureMouseDown}
                  onMouseUp={handleTemperatureMouseUp}
                />
              </div>
            </div>

            <div className={hyperparametersControl}>
              <Label>Top P:</Label>
              <div className={sliderContainer}>
                <Slider
                  min={0}
                  max={1}
                  step={0.1}
                  value={topP}
                  onChange={setTopP}
                  onMouseDown={handleTopPMouseDown}
                  onMouseUp={handleTopPMouseUp}
                />
              </div>
            </div>

            <div className={hyperparametersControl}>
              <Label>Top K:</Label>
              <div className={sliderContainer}>
                <Slider
                  min={1}
                  max={50}
                  step={1}
                  value={topK}
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
