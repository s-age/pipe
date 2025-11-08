import { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Checkbox from '@/components/atoms/Checkbox'
import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import { SessionBasicMetaForm } from '@/components/organisms/SessionBasicMetaForm'
import { useTodoActions } from '@/components/organisms/SessionMeta/useTodoActions'
import { SessionReferencesList } from '@/components/organisms/SessionReferencesList'
import {
  editSessionMeta,
  EditSessionMetaRequest,
} from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'
import { Actions } from '@/stores/useChatHistoryStore'
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
import { useSessionMetaLogic } from './useSessionMetaLogic'

type UseSessionMetaSaverProps = {
  actions: Actions
}

const useSessionMetaSaver = ({
  actions,
}: UseSessionMetaSaverProps): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const { setError, refreshSessions } = actions

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest,
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await refreshSessions()
      setError(null)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to save session meta.')
    }
  }

  return { handleMetaSave }
}

type SessionMetaProps = {
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
}: SessionMetaProps): JSX.Element => {
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
            <Label className={checkboxLabel}>
              <Checkbox
                name="multi_step_reasoning"
                checked={sessionDetail.multi_step_reasoning_enabled}
                onChange={handleMultiStepReasoningChange}
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
                        onChange={() =>
                          currentSessionId &&
                          handleTodoCheckboxChange(
                            currentSessionId,
                            sessionDetail.todos,
                            index,
                          )
                        }
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
