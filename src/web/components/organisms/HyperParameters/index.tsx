import React from 'react'

import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Slider } from '@/components/molecules/Slider'
import { useSessionMetaSaver } from '@/components/organisms/SessionMeta/useSessionMetaSaver'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Actions } from '@/stores/useChatHistoryStore'

import { useHyperParametersHandlers } from './hooks/useHyperParametersHandlers'
import { metaItem, hyperparametersControl, sliderContainer } from './style.css'

type HyperParametersProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  actions: Actions
}

export const HyperParameters = ({
  sessionDetail,
  currentSessionId,
  actions,
}: HyperParametersProperties): React.JSX.Element => {
  useSessionMetaSaver({ actions })

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
    handleTopKMouseDown,
  } = useHyperParametersHandlers({
    sessionDetail,
    currentSessionId,
    onMetaSave: (_id, meta) => {
      // Update local store immediately with authoritative hyperparameters from server
      if (sessionDetail && meta.hyperparameters)
        actions.setSessionDetail({
          ...sessionDetail,
          hyperparameters: meta.hyperparameters,
        })
    },
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
