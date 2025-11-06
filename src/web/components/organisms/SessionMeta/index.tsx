import React, { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Checkbox from '@/components/atoms/Checkbox'
import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import { SessionBasicMetaForm } from '@/components/organisms/SessionBasicMetaForm'
import { useTodoActions } from '@/components/organisms/SessionMeta/useTodoActions'
import { SessionReferencesList } from '@/components/organisms/SessionReferencesList'
import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'
import { Todo } from '@/types/todo'

import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  checkboxLabel,
  hyperparametersControl,
  sliderValue,
  todosList,
  todoItem,
  todoCheckboxLabel,
  todoTitle,
  noItemsMessage,
  stickySaveMetaButtonContainer,
  metaItem,
  metaItemLabel,
  todoCheckboxMargin,
} from './style.css'
import { useSessionHyperparameters } from './useSessionHyperparameters'

type SessionMetaProps = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
  setSessionDetail: (data: SessionDetail | null) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
  setSessionDetail,
  setError,
  refreshSessions,
}: SessionMetaProps): JSX.Element => {
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
  } = useSessionHyperparameters({ sessionDetail, currentSessionId, onMetaSave })

  const { handleUpdateTodo, handleDeleteAllTodos } = useTodoActions(
    setSessionDetail,
    setError,
    refreshSessions,
  )

  const handleSaveMeta = (): void => {
    if (!currentSessionId || !sessionDetail) return
    const meta: EditSessionMetaRequest = {
      multi_step_reasoning_enabled: sessionDetail.multi_step_reasoning_enabled, // これはチェックボックスなので即時反映
      hyperparameters: {
        temperature: temperature,
        top_p: topP,
        top_k: topK,
      },
    }
    onMetaSave(currentSessionId, meta)
  }

  const handleTodoCheckboxChange = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newTodos = [...sessionDetail.todos]
    newTodos[index].checked = !newTodos[index].checked
    handleUpdateTodo(currentSessionId, newTodos)
  }

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
          <SessionBasicMetaForm
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            onMetaSave={onMetaSave}
          />

          <SessionReferencesList
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            setError={setError}
            refreshSessions={refreshSessions}
          />

          <div className={metaItem}>
            <Label className={checkboxLabel}>
              <Checkbox
                name="multi_step_reasoning"
                checked={sessionDetail.multi_step_reasoning_enabled}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onMetaSave(currentSessionId, {
                    multi_step_reasoning_enabled: e.target.checked,
                  })
                }
              />
              <strong>Multi-step Reasoning</strong>
            </Label>
          </div>
          <div className={metaItem}>
            <Label className={metaItemLabel}>Hyperparameters:</Label>
            <div className={hyperparametersControl}>
              <Label>Temperature:</Label>
              <div>
                <span className={sliderValue}>{temperature}</span>
                <InputText
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={temperature}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setTemperature(parseFloat(e.target.value))
                  }
                  onMouseUp={handleTemperatureMouseUp}
                />
              </div>
            </div>
            <div className={hyperparametersControl}>
              <Label>Top P:</Label>
              <div>
                <span className={sliderValue}>{topP}</span>
                <InputText
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={topP}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setTopP(parseFloat(e.target.value))
                  }
                  onMouseUp={handleTopPMouseUp}
                />
              </div>
            </div>
            <div className={hyperparametersControl}>
              <Label>Top K:</Label>
              <div>
                <span className={sliderValue}>{topK}</span>
                <InputText
                  type="range"
                  min="1"
                  max="50"
                  step="1"
                  value={topK}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setTopK(parseInt(e.target.value, 10))
                  }
                  onMouseUp={handleTopKMouseUp}
                />
              </div>
            </div>
          </div>
          <div className={metaItem}>
            <Label className={metaItemLabel}>Todos:</Label>
            <Button
              kind="secondary"
              size="default"
              onClick={() => currentSessionId && handleDeleteAllTodos(currentSessionId)}
            >
              Delete All
            </Button>
            {sessionDetail.todos.length > 0 ? (
              <ul className={todosList}>
                {sessionDetail.todos.map((todo: Todo, index: number) => (
                  <li key={index} className={todoItem}>
                    <Label className={todoCheckboxLabel}>
                      <Checkbox
                        checked={todo.checked}
                        onChange={() => handleTodoCheckboxChange(index)}
                        className={todoCheckboxMargin}
                      />
                      <strong className={todoTitle}>{todo.title}</strong>
                    </Label>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={noItemsMessage}>No todos for this session.</p>
            )}
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
