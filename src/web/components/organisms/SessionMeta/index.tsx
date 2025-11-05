import clsx from 'clsx'
import React, { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Checkbox from '@/components/atoms/Checkbox'
import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import TextArea from '@/components/atoms/TextArea'
import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'
import { Reference } from '@/types/reference'
import { Todo } from '@/types/todo'

import {
  metaColumn,
  sessionMetaSection,
  sessionMetaView,
  metaItem,
  metaItemLabel,
  inputFullWidth,
  textareaFullWidth,
  checkboxLabel,
  hyperparametersControl,
  sliderValue,
  todosList,
  todoItem,
  todoCheckboxLabel,
  todoTitle,
  noItemsMessage,
  referencesList,
  referenceItem,
  referenceControls,
  referenceLabel,
  referencePath,
  materialIcons,
  ttlControls,
  ttlValue,
  referenceCheckboxMargin,
  stickySaveMetaButtonContainer,
  lockIconStyle,
} from './style.css'
import { useSessionBasicMeta } from './useSessionBasicMeta'
import { useSessionHyperparameters } from './useSessionHyperparameters'
import { colors } from '../../../styles/colors.css'

type SessionMetaProps = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
  onUpdateTodo: (sessionId: string, todos: Todo[]) => void
  onDeleteAllTodos: (sessionId: string) => void
  onUpdateReferencePersist: (sessionId: string, index: number, persist: boolean) => void
  onUpdateReferenceTtl: (sessionId: string, index: number, ttl: number) => void
  onUpdateReferenceDisabled: (
    sessionId: string,
    index: number,
    disabled: boolean,
  ) => void
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
  onUpdateTodo,
  onDeleteAllTodos,
  onUpdateReferencePersist,
  onUpdateReferenceTtl,
  onUpdateReferenceDisabled,
}: SessionMetaProps): JSX.Element => {
  const {
    purpose,
    setPurpose,
    handlePurposeBlur,
    background,
    setBackground,
    handleBackgroundBlur,
    roles,
    setRoles,
    handleRolesBlur,
    procedure,
    setProcedure,
    handleProcedureBlur,
    artifacts,
    setArtifacts,
    handleArtifactsBlur,
  } = useSessionBasicMeta({ sessionDetail, currentSessionId, onMetaSave })

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

  const handleSaveMeta = (): void => {
    if (!currentSessionId || !sessionDetail) return
    const meta: EditSessionMetaRequest = {
      purpose: purpose,
      background: background,
      roles: roles
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      procedure: procedure,
      artifacts: artifacts
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
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
    onUpdateTodo(currentSessionId, newTodos)
  }

  const handleReferenceCheckboxChange = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].disabled = !newReferences[index].disabled
    onUpdateReferenceDisabled(currentSessionId, index, newReferences[index].disabled)
  }

  const handleReferencePersistToggle = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].persist = !newReferences[index].persist
    onUpdateReferencePersist(currentSessionId, index, newReferences[index].persist)
  }

  const handleReferenceTtlChange = (
    index: number,
    action: 'increment' | 'decrement',
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3
    const newTtl =
      action === 'increment'
        ? (currentTtl || 0) + 1
        : Math.max(0, (currentTtl || 0) - 1)
    newReferences[index].ttl = newTtl
    onUpdateReferenceTtl(currentSessionId, index, newTtl)
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
          <div className={metaItem}>
            <Label htmlFor="purpose" className={metaItemLabel}>
              Purpose:
            </Label>
            <InputText
              id="purpose"
              value={purpose}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setPurpose(e.target.value)
              }
              onBlur={handlePurposeBlur}
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="background" className={metaItemLabel}>
              Background:
            </Label>
            <TextArea
              id="background"
              value={background}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setBackground(e.target.value)
              }
              onBlur={handleBackgroundBlur}
              className={textareaFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="roles" className={metaItemLabel}>
              Roles:
            </Label>
            <InputText
              id="roles"
              value={roles}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setRoles(e.target.value)
              }
              onBlur={handleRolesBlur}
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="procedure" className={metaItemLabel}>
              Procedure:
            </Label>
            <InputText
              id="procedure"
              value={procedure}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setProcedure(e.target.value)
              }
              onBlur={handleProcedureBlur}
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="artifacts" className={metaItemLabel}>
              Artifacts:
            </Label>
            <InputText
              id="artifacts"
              value={artifacts}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setArtifacts(e.target.value)
              }
              onBlur={handleArtifactsBlur}
              className={inputFullWidth}
            />
          </div>

          <div className={metaItem}>
            <Label className={metaItemLabel}>References:</Label>
            {sessionDetail.references.length > 0 ? (
              <ul className={referencesList}>
                {sessionDetail.references.map((reference: Reference, index: number) => (
                  <li key={index} className={referenceItem}>
                    <div className={referenceControls}>
                      <Label className={referenceLabel}>
                        <Checkbox
                          checked={!reference.disabled}
                          onChange={() => handleReferenceCheckboxChange(index)}
                          className={referenceCheckboxMargin}
                        />
                        <Button
                          kind="ghost"
                          size="xsmall"
                          style={{ minWidth: '32px' }}
                          onClick={() => handleReferencePersistToggle(index)}
                        >
                          <span
                            className={clsx(materialIcons, lockIconStyle)}
                            data-locked={reference.persist}
                          >
                            {reference.persist ? 'lock' : 'lock_open'}
                          </span>
                        </Button>
                        <span
                          data-testid="reference-path"
                          className={referencePath}
                          style={{
                            textDecoration: reference.disabled
                              ? 'line-through'
                              : 'none',
                            color: reference.disabled ? colors.grayText : 'inherit',
                          }}
                        >
                          {reference.path}
                        </span>
                      </Label>
                      <div className={ttlControls}>
                        <Button
                          kind="primary"
                          size="xsmall"
                          onClick={() => handleReferenceTtlChange(index, 'decrement')}
                        >
                          -
                        </Button>
                        <span className={ttlValue}>
                          {reference.ttl !== null ? reference.ttl : 3}
                        </span>
                        <Button
                          kind="primary"
                          size="xsmall"
                          onClick={() => handleReferenceTtlChange(index, 'increment')}
                        >
                          +
                        </Button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className={noItemsMessage}>No references for this session.</p>
            )}
          </div>

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
              onClick={() => currentSessionId && onDeleteAllTodos(currentSessionId)}
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
                        className={referenceCheckboxMargin}
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
