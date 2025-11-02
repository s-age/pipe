import React, { useState } from 'react';

import { marked } from 'marked';
import Button from '@/components/atoms/Button';
import { turnHeader, turnHeaderInfo, turnIndexStyle, turnTimestamp, turnHeaderControls, turnContent, rawMarkdown, renderedMarkdown, toolResponseContent, statusSuccess, statusError, editablePre, editTextArea, editButtonContainer, turnWrapper, userTaskAligned, otherTurnAligned, turnContentBase } from './style.css';

interface TurnProps {
  turn: any; // TODO: 型を定義する
  index: number;
  sessionId: string;
  expertMode: boolean;
  onDeleteTurn: (sessionId: string, turnIndex: number) => void;
  onForkSession: (sessionId: string, forkIndex: number) => void;
}

const Turn: React.FC<TurnProps> = ({ turn, index, sessionId, expertMode, onDeleteTurn, onForkSession }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(turn.content || turn.instruction || '');

  const getHeaderContent = (type: string) => {
    switch (type) {
      case 'user_task': return 'You';
      case 'model_response': return 'Model';
      case 'function_calling': return 'Function Calling';
      case 'tool_response': return 'Tool Response';
      case 'compressed_history': return 'Compressed';
      default: return 'Unknown';
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedContent);
      alert('Copied!');
    } catch (err) {
      console.error('Failed to copy: ', err);
      alert('Failed to copy');
    }
  };

  const handleSaveEdit = () => {
    // TODO: API呼び出しを実装する
    console.log(`Saving turn ${index} with new content: ${editedContent}`);
    setIsEditing(false);
  };

  const renderTurnContent = () => {
    if (isEditing) {
      return (
        <div className={turnContent}>
          <textarea
            className={editTextArea}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
          />
          <div className={editButtonContainer}>
            <Button onClick={handleSaveEdit}>Save</Button>
            <Button variant="cancel" onClick={() => setIsEditing(false)}>Cancel</Button>
          </div>
        </div>
      );
    }

    switch (turn.type) {
      case 'user_task':
        return <pre className={editablePre}>{turn.instruction}</pre>;
      case 'model_response':
      case 'compressed_history':
        const markdownContent = turn.content || '';
        return (
          <div className={turnContent}>
            {turn.type === 'compressed_history' && <p><strong><em>-- History Compressed --</em></strong></p>}
            <div className={rawMarkdown}>{markdownContent}</div>
            <div
              className={`${renderedMarkdown} markdown-body`}
              dangerouslySetInnerHTML={{ __html: marked.parse(markdownContent.trim()) }}
            />
          </div>
        );
      case 'function_calling':
        return <pre className={turnContent}>{turn.response}</pre>;
      case 'tool_response':
        const statusClass = turn.response.status === 'success' ? statusSuccess : statusError;
        return (
          <div className={toolResponseContent}>
            <strong>Status: </strong>
            <span className={statusClass}>{turn.response.status}</span>
            {turn.response.output && <pre>{JSON.stringify(turn.response.output, null, 2)}</pre>}
          </div>
        );
      default:
        return <pre className={turnContent}>{JSON.stringify(turn, null, 2)}</pre>;
    }
  };

  const formatTimestamp = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  };

  const timestamp = turn.timestamp ? formatTimestamp(new Date(turn.timestamp)) : '';

  return (
    <div className={`${turnWrapper} ${turn.type === 'user_task' ? userTaskAligned : otherTurnAligned}`}>
      <div className={turnContentBase} id={`turn-${index}`}>
        <div className={turnHeader}>
        <span className={turnHeaderInfo}>
          <span className={turnIndexStyle}>{index + 1}:</span>
          {getHeaderContent(turn.type)}
          <span className={turnTimestamp}>{timestamp}</span>
        </span>
        <div className={turnHeaderControls}>
          {turn.type === 'model_response' && (
            <Button onClick={() => onForkSession(sessionId, index)}>Fork</Button>
          )}
          <Button onClick={handleCopy}>Copy</Button>
          {expertMode && (turn.type === 'user_task' || turn.type === 'model_response') && (
            <Button onClick={() => setIsEditing(true)}>Edit</Button>
          )}
          <Button variant="cancel" onClick={() => onDeleteTurn(sessionId, index)}>Delete</Button>
        </div>
      </div>
      {renderTurnContent()}
        </div>
    </div>
  );
};

export default Turn;