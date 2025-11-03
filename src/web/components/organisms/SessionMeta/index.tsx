import clsx from 'clsx'
import React, { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Checkbox from '@/components/atoms/Checkbox'
import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import TextArea from '@/components/atoms/TextArea'

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
import { colors } from '../../../styles/colors.css'

type TodoItem = {
  title: string
  checked: boolean
}

type ReferenceItem = {
  path: string
  persist: boolean
  ttl: number | null
  disabled: boolean
}

type SessionData = {
  purpose: string
  background: string
  roles: string[]
  procedure: string
  artifacts: string[]
  multi_step_reasoning_enabled: boolean
  hyperparameters: {
    temperature: { value: number }
    top_p: { value: number }
    top_k: { value: number }
  }
  todos: TodoItem[]
  references: ReferenceItem[]
}

type SessionMetaProps = {
  sessionData: SessionData | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: SessionData) => void
  onUpdateTodo: (sessionId: string, todos: TodoItem[]) => void
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
  sessionData,
  currentSessionId,
  onMetaSave,
  onUpdateTodo,
  onDeleteAllTodos,
  onUpdateReferencePersist,
  onUpdateReferenceTtl,
  onUpdateReferenceDisabled,
}: SessionMetaProps): JSX.Element => {
  const handleSaveMeta = () => {
    if (!currentSessionId || !sessionData) return
    const meta = {
      purpose: sessionData.purpose,
      background: sessionData.background,
      roles: sessionData.roles,
      procedure: sessionData.procedure,
      artifacts: sessionData.artifacts,
      multi_step_reasoning_enabled: sessionData.multi_step_reasoning_enabled,
      hyperparameters: {
        temperature: { value: sessionData.hyperparameters.temperature.value },
        top_p: { value: sessionData.hyperparameters.top_p.value },
        top_k: { value: sessionData.hyperparameters.top_k.value },
      },
      todos: sessionData.todos,
      references: sessionData.references,
    }
    onMetaSave(currentSessionId, meta)
  }

  const handleTodoCheckboxChange = (index: number) => {
    if (!currentSessionId || !sessionData) return
    const newTodos = [...sessionData.todos]
    newTodos[index].checked = !newTodos[index].checked
    onUpdateTodo(currentSessionId, newTodos)
  }

  const handleReferenceCheckboxChange = (index: number) => {
    if (!currentSessionId || !sessionData) return
    const newReferences = [...sessionData.references]
    newReferences[index].disabled = !newReferences[index].disabled
    onUpdateReferenceDisabled(currentSessionId, index, newReferences[index].disabled)
  }

  const handleReferencePersistToggle = (index: number) => {
    if (!currentSessionId || !sessionData) return
    const newReferences = [...sessionData.references]
    newReferences[index].persist = !newReferences[index].persist
    onUpdateReferencePersist(currentSessionId, index, newReferences[index].persist)
  }

  const handleReferenceTtlChange = (
    index: number,
    action: 'increment' | 'decrement',
  ) => {
    if (!currentSessionId || !sessionData) return
    const newReferences = [...sessionData.references]
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3
    const newTtl = action === 'increment' ? currentTtl + 1 : Math.max(0, currentTtl - 1)
    newReferences[index].ttl = newTtl
    onUpdateReferenceTtl(currentSessionId, index, newTtl)
  }

  if (!currentSessionId || !sessionData) {
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
              value={sessionData.purpose}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onMetaSave(currentSessionId, {
                  ...sessionData,
                  purpose: e.target.value,
                })
              }
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="background" className={metaItemLabel}>
              Background:
            </Label>
            <TextArea
              id="background"
              value={sessionData.background}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                onMetaSave(currentSessionId, {
                  ...sessionData,
                  background: e.target.value,
                })
              }
              className={textareaFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="roles" className={metaItemLabel}>
              Roles:
            </Label>
            <InputText
              id="roles"
              value={sessionData.roles?.join(', ') || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onMetaSave(currentSessionId, {
                  ...sessionData,
                  roles: e.target.value
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="procedure" className={metaItemLabel}>
              Procedure:
            </Label>
            <InputText
              id="procedure"
              value={sessionData.procedure}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onMetaSave(currentSessionId, {
                  ...sessionData,
                  procedure: e.target.value,
                })
              }
              className={inputFullWidth}
            />
          </div>
          <div className={metaItem}>
            <Label htmlFor="artifacts" className={metaItemLabel}>
              Artifacts:
            </Label>
            <InputText
              id="artifacts"
              value={sessionData.artifacts?.join(', ') || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                onMetaSave(currentSessionId, {
                  ...sessionData,
                  artifacts: e.target.value
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
              className={inputFullWidth}
            />
          </div>

          <div className={metaItem}>
            <Label className={metaItemLabel}>References:</Label>
            {sessionData.references.length > 0 ? (
              <ul className={referencesList}>
                {sessionData.references.map(
                  (reference: ReferenceItem, index: number) => (
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
                  ),
                )}
              </ul>
            ) : (
              <p className={noItemsMessage}>No references for this session.</p>
            )}
          </div>

          <div className={metaItem}>
            <Label className={checkboxLabel}>
              <Checkbox
                name="multi_step_reasoning"
                checked={sessionData.multi_step_reasoning_enabled}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  onMetaSave(currentSessionId, {
                    ...sessionData,
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
                <span className={sliderValue}>
                  {sessionData.hyperparameters?.temperature?.value || 0.7}
                </span>
                <InputText
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={sessionData.hyperparameters?.temperature?.value || 0.7}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    onMetaSave(currentSessionId, {
                      ...sessionData,
                      hyperparameters: {
                        ...sessionData.hyperparameters,
                        temperature: { value: parseFloat(e.target.value) },
                      },
                    })
                  }
                />
              </div>
            </div>
            <div className={hyperparametersControl}>
              <Label>Top P:</Label>
              <div>
                <span className={sliderValue}>
                  {sessionData.hyperparameters?.top_p?.value || 0.9}
                </span>
                <InputText
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={sessionData.hyperparameters?.top_p?.value || 0.9}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    onMetaSave(currentSessionId, {
                      ...sessionData,
                      hyperparameters: {
                        ...sessionData.hyperparameters,
                        top_p: { value: parseFloat(e.target.value) },
                      },
                    })
                  }
                />
              </div>
            </div>
            <div className={hyperparametersControl}>
              <Label>Top K:</Label>
              <div>
                <span className={sliderValue}>
                  {sessionData.hyperparameters?.top_k?.value || 5}
                </span>
                <InputText
                  type="range"
                  min="1"
                  max="50"
                  step="1"
                  value={sessionData.hyperparameters?.top_k?.value || 5}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    onMetaSave(currentSessionId, {
                      ...sessionData,
                      hyperparameters: {
                        ...sessionData.hyperparameters,
                        top_k: { value: parseInt(e.target.value, 10) },
                      },
                    })
                  }
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
            {sessionData.todos.length > 0 ? (
              <ul className={todosList}>
                {sessionData.todos.map((todo: TodoItem, index: number) => (
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
