import clsx from "clsx";
import React, { useState, useEffect, JSX } from "react";

import Button from "@/components/atoms/Button";
import Checkbox from "@/components/atoms/Checkbox";
import InputText from "@/components/atoms/InputText";
import Label from "@/components/atoms/Label";
import TextArea from "@/components/atoms/TextArea";

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
} from "./style.css";
import { colors } from "../../../styles/colors.css";

type SessionMetaProps = {
  sessionData: any; // TODO: 型を定義する
  currentSessionId: string | null;
  onMetaSave: (sessionId: string, meta: any) => void;
  onUpdateTodo: (sessionId: string, todos: any[]) => void;
  onDeleteAllTodos: (sessionId: string) => void;
  onUpdateReferencePersist: (
    sessionId: string,
    index: number,
    persist: boolean,
  ) => void;
  onUpdateReferenceTtl: (sessionId: string, index: number, ttl: number) => void;
  onUpdateReferenceDisabled: (
    sessionId: string,
    index: number,
    disabled: boolean,
  ) => void;
};

const SessionMeta: ({
  sessionData,
  currentSessionId,
  onMetaSave,
  onUpdateTodo,
  onDeleteAllTodos,
  onUpdateReferencePersist,
  onUpdateReferenceTtl,
  onUpdateReferenceDisabled,
}: SessionMetaProps) => JSX.Element = ({
  sessionData,
  currentSessionId,
  onMetaSave,
  onUpdateTodo,
  onDeleteAllTodos,
  onUpdateReferencePersist,
  onUpdateReferenceTtl,
  onUpdateReferenceDisabled,
}) => {
  const [purpose, setPurpose] = useState(sessionData?.purpose || "");
  const [background, setBackground] = useState(sessionData?.background || "");
  const [roles, setRoles] = useState(sessionData?.roles?.join(", ") || "");
  const [procedure, setProcedure] = useState(sessionData?.procedure || "");
  const [artifacts, setArtifacts] = useState(sessionData?.artifacts?.join(", ") || "");
  const [multiStepReasoningEnabled, setMultiStepReasoningEnabled] = useState(
    sessionData?.multi_step_reasoning_enabled || false,
  );
  const [temperature, setTemperature] = useState(
    sessionData?.hyperparameters?.temperature?.value || 0.7,
  );
  const [topP, setTopP] = useState(sessionData?.hyperparameters?.top_p?.value || 0.9);
  const [topK, setTopK] = useState(sessionData?.hyperparameters?.top_k?.value || 5);
  const [todos, setTodos] = useState(sessionData?.todos || []);
  const [references, setReferences] = useState(sessionData?.references || []);

  useEffect(() => {
    if (sessionData) {
      setPurpose(sessionData.purpose || "");
      setBackground(sessionData.background || "");
      setRoles(sessionData.roles?.join(", ") || "");
      setProcedure(sessionData.procedure || "");
      setArtifacts(sessionData.artifacts?.join(", ") || "");
      setMultiStepReasoningEnabled(sessionData.multi_step_reasoning_enabled || false);
      setTemperature(sessionData.hyperparameters?.temperature?.value || 0.7);
      setTopP(sessionData.hyperparameters?.top_p?.value || 0.9);
      setTopK(sessionData.hyperparameters?.top_k?.value || 5);
      setTodos(sessionData.todos || []);
      setReferences(sessionData.references || []);
    }
  }, [sessionData]);

  const handleSaveMeta = () => {
    if (!currentSessionId) return;
    const meta = {
      purpose,
      background,
      roles: roles
        .split(",")
        .map((s: string) => s.trim())
        .filter(Boolean),
      procedure,
      artifacts: artifacts
        .split(",")
        .map((s: string) => s.trim())
        .filter(Boolean),
      multi_step_reasoning_enabled: multiStepReasoningEnabled,
      hyperparameters: {
        temperature: { value: parseFloat(temperature.toString()) },
        top_p: { value: parseFloat(topP.toString()) },
        top_k: { value: parseInt(topK.toString(), 10) },
      },
    };
    onMetaSave(currentSessionId, meta);
  };

  const handleTodoCheckboxChange = (index: number) => {
    if (!currentSessionId) return;
    const newTodos = [...todos];
    newTodos[index].checked = !newTodos[index].checked;
    setTodos(newTodos);
    onUpdateTodo(currentSessionId, newTodos);
  };

  const handleReferenceCheckboxChange = (index: number) => {
    if (!currentSessionId) return;
    const newReferences = [...references];
    newReferences[index].disabled = !newReferences[index].disabled;
    setReferences(newReferences);
    onUpdateReferenceDisabled(currentSessionId, index, newReferences[index].disabled);
  };

  const handleReferencePersistToggle = (index: number) => {
    if (!currentSessionId) return;
    const newReferences = [...references];
    newReferences[index].persist = !newReferences[index].persist;
    setReferences(newReferences);
    onUpdateReferencePersist(currentSessionId, index, newReferences[index].persist);
  };

  const handleReferenceTtlChange = (
    index: number,
    action: "increment" | "decrement",
  ) => {
    if (!currentSessionId) return;
    const newReferences = [...references];
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3;
    const newTtl =
      action === "increment" ? currentTtl + 1 : Math.max(0, currentTtl - 1);
    newReferences[index].ttl = newTtl;
    setReferences(newReferences);
    onUpdateReferenceTtl(currentSessionId, index, newTtl);
  };

  if (!currentSessionId || !sessionData) {
    return (
      <div className={metaColumn}>
        <p className={noItemsMessage}>Select a session to view its meta information.</p>
      </div>
    );
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
              className={inputFullWidth}
            />
          </div>

          <div className={metaItem}>
            <Label className={metaItemLabel}>References:</Label>
            {references.length > 0 ? (
              <ul className={referencesList}>
                {references.map((reference: any, index: number) => (
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
                          style={{ minWidth: "32px" }}
                          onClick={() => handleReferencePersistToggle(index)}
                        >
                          <span
                            className={clsx(materialIcons, lockIconStyle)}
                            data-locked={reference.persist}
                          >
                            {reference.persist ? "lock" : "lock_open"}
                          </span>
                        </Button>
                        <span
                          data-testid="reference-path"
                          className={referencePath}
                          style={{
                            textDecoration: reference.disabled
                              ? "line-through"
                              : "none",
                            color: reference.disabled ? colors.grayText : "inherit",
                          }}
                        >
                          {reference.path}
                        </span>
                      </Label>
                      <div className={ttlControls}>
                        <Button
                          kind="primary"
                          size="xsmall"
                          onClick={() => handleReferenceTtlChange(index, "decrement")}
                        >
                          -
                        </Button>
                        <span className={ttlValue}>
                          {reference.ttl !== null ? reference.ttl : 3}
                        </span>
                        <Button
                          kind="primary"
                          size="xsmall"
                          onClick={() => handleReferenceTtlChange(index, "increment")}
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
                checked={multiStepReasoningEnabled}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setMultiStepReasoningEnabled(e.target.checked)
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
            {todos.length > 0 ? (
              <ul className={todosList}>
                {todos.map((todo: any, index: number) => (
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
  );
};

export default SessionMeta;
