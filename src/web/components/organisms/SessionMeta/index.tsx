import React, { useCallback } from 'react'

import { Button } from '@/components/atoms/Button'
import { Checkbox } from '@/components/atoms/Checkbox'
import { InputCheckbox } from '@/components/atoms/InputCheckbox'
import { Label } from '@/components/atoms/Label'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Slider } from '@/components/molecules/Slider'
import { SessionBasicMetaForm } from '@/components/organisms/SessionBasicMetaForm'
import { useTodoActions } from '@/components/organisms/SessionMeta/useTodoActions'
import { SessionReferencesList } from '@/components/organisms/SessionReferencesList'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Actions } from '@/stores/useChatHistoryStore'
import type { Todo } from '@/types/todo'

import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'
import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  hyperparametersControl,
  sliderContainer,
  todosList,
  todoItem,
  todoCheckboxLabel,
  todoTitle,
  noItemsMessage,
  stickySaveMetaButtonContainer,
  metaItem,
  deleteTodosButton,
  multiStepLabel,
  todoCheckboxMargin,
} from './style.css'
import { useSessionHyperparameters } from './useSessionHyperparameters'
import { useSessionMetaLogic } from './useSessionMetaLogic'
import { useSessionMetaSaver } from './useSessionMetaSaver'

// `useSessionMetaSaver` extracted to its own hook file for reuse and testability

type SessionMetaProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
  actions: Actions
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  setError,
  refreshSessions,
  actions,
}: SessionMetaProperties): React.JSX.Element => {
  const { handleMetaSave } = useSessionMetaSaver({ actions })

  const {
    temperature,
    setTemperature,
    handleTemperatureMouseUp,
    topP,
    setTopP,
    handleTopPMouseUp,
    topK,
    setTopK,
    handleTopKMouseUp,
  } = useSessionHyperparameters({
    sessionDetail,
    currentSessionId,
    onMetaSave: handleMetaSave,
  })
  const handleSliderTemperatureChange = useCallback(
    (v: number): void => {
      setTemperature(v)
    },
    [setTemperature],
  )

  const handleSliderTopPChange = useCallback(
    (v: number): void => {
      setTopP(v)
    },
    [setTopP],
  )

  const handleSliderTopKChange = useCallback(
    (v: number): void => {
      setTopK(v)
    },
    [setTopK],
  )
  const { handleDeleteAllTodos, handleTodoCheckboxChange } = useTodoActions(
    setSessionDetail,
    setError,
    refreshSessions,
  )

  const { handleSaveMeta, handleMultiStepReasoningChange } = useSessionMetaLogic({
    sessionDetail,
    currentSessionId,
    onMetaSave: handleMetaSave,
    temperature,
    topP,
    topK,
  })

  const { handleDeleteAll, handleTodoCheckboxChangeWrapper } = useSessionMetaHandlers({
    currentSessionId,
    sessionDetail,
    handleDeleteAllTodos,
    handleTodoCheckboxChange,
    setTemperature,
    setTopP,
    setTopK,
  })

  if (!currentSessionId || !sessionDetail) {
    return (
      <div className={metaColumn}>
        <p className={noItemsMessage}>Select a session to view its meta information.</p>
      </div>
    )
  }

  return (
    <div className={metaColumn}>
      <input type="hidden" id="current-session-id" value={currentSessionId} />
      <section className={sessionMetaSection}>
        <div className={sessionMetaView}>
          <SessionBasicMetaForm sessionDetail={sessionDetail} />

          <SessionReferencesList
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            setError={setError}
            refreshSessions={refreshSessions}
          />

          <div className={metaItem}>
            <InputCheckbox
              name="multi_step_reasoning"
              checked={sessionDetail.multi_step_reasoning_enabled}
              onChange={handleMultiStepReasoningChange}
            >
              <strong className={multiStepLabel}>Multi-step Reasoning</strong>
            </InputCheckbox>
          </div>
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
                        onChange={handleSliderTemperatureChange}
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
                        onChange={handleSliderTopPChange}
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
                        onChange={handleSliderTopKChange}
                        onMouseUp={handleTopKMouseUp}
                      />
                    </div>
                  </div>
                </div>
              )}
            </Fieldset>
          </div>
          <div className={metaItem}>
            <Fieldset legend="Todos">
              {() => (
                <div>
                  <Button
                    className={deleteTodosButton}
                    kind="secondary"
                    size="default"
                    onClick={handleDeleteAll}
                  >
                    Delete All
                  </Button>

                  {sessionDetail.todos.length > 0 ? (
                    <ul className={todosList}>
                      {sessionDetail.todos.map((todo: Todo, index: number) => (
                        <li key={index} className={todoItem}>
                          <div className={todoCheckboxLabel}>
                            <div className={todoCheckboxMargin}>
                              <Checkbox
                                checked={todo.checked}
                                onChange={handleTodoCheckboxChangeWrapper}
                                data-index={String(index)}
                              />
                            </div>
                            <strong className={todoTitle}>{todo.title}</strong>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className={noItemsMessage}>No todos for this session.</p>
                  )}
                </div>
              )}
            </Fieldset>
          </div>
        </div>
      </section>

      <div className={stickySaveMetaButtonContainer}>
        <Button kind="primary" size="default" onClick={handleSaveMeta}>
          Save Meta
        </Button>
      </div>
    </div>
  )
}
