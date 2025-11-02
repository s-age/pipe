import React, { useState, useEffect } from 'react';
import { fetchSessions, fetchSessionData, updateSessionMeta, deleteTurn, forkSession, sendInstruction, updateTodo, deleteTodos, updateReferencePersist, updateReferenceTtl, updateReferenceDisabled } from '@/lib/api_client/client';
import SessionList from '@/components/organisms/SessionList';
import TurnsList from '@/components/organisms/TurnsList';
import SessionMeta from '@/components/organisms/SessionMeta';
import { appContainer } from './HomePage.css';

const HomePage: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]); // TODO: 型を定義する
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessionData, setSessionData] = useState<any>(null); // TODO: 型を定義する
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const expertMode = true; // 仮の値

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const fetchedSessions = await fetchSessions();
        setSessions(fetchedSessions);
        // URLからセッションIDを取得し、現在のセッションを設定
        const pathParts = window.location.pathname.split('/');
        const id = pathParts[pathParts.length - 1];
        if (id && id !== 'session' && id !== '') {
          setCurrentSessionId(id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load sessions.');
      } finally {
        setLoading(false);
      }
    };
    loadSessions();
  }, []);

  useEffect(() => {
    const loadSessionData = async () => {
      if (currentSessionId) {
        setLoading(true);
        try {
          const data = await fetchSessionData(currentSessionId);
          setSessionData(data.session);
        } catch (err: any) {
          setError(err.message || 'Failed to load session data.');
        } finally {
          setLoading(false);
        }
      } else {
        setSessionData(null);
      }
    };
    loadSessionData();
  }, [currentSessionId]);

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    window.history.pushState({}, '', `/session/${sessionId}`);
  };

  const handleMetaSave = async (id: string, meta: any) => {
    try {
      await updateSessionMeta(id, meta);
      alert('Session meta saved successfully!');
      // 必要に応じてセッションデータを再読み込み
      if (currentSessionId === id) {
        const data = await fetchSessionData(id);
        setSessionData(data.session);
      }
      const fetchedSessions = await fetchSessions();
      setSessions(fetchedSessions);
    } catch (err: any) {
      setError(err.message || 'Failed to save session meta.');
    }
  };

  const handleDeleteTurn = async (sessionId: string, turnIndex: number) => {
    if (!confirm('Are you sure you want to delete this turn?')) return;
    try {
      await deleteTurn(sessionId, turnIndex);
      alert('Turn deleted successfully!');
      // セッションデータを再読み込み
      const data = await fetchSessionData(sessionId);
      setSessionData(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to delete turn.');
    }
  };

  const handleForkSession = async (sessionId: string, forkIndex: number) => {
    if (!confirm(`Are you sure you want to fork this session at turn index ${forkIndex + 1}?`)) return;
    try {
      const result = await forkSession(sessionId, forkIndex);
      if (result.success && result.new_session_id) {
        window.location.href = `/session/${result.new_session_id}`;
      } else {
        throw new Error(result.message || 'Failed to fork session.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fork session.');
    }
  };

  const handleSendInstruction = async (sessionId: string, instruction: string) => {
    try {
      // リアルタイム更新のために、まずUIにユーザーのターンとモデルの応答のプレースホルダーを追加
      // これは複雑なので、一旦API呼び出しのみに留める
      await sendInstruction(sessionId, instruction);
      // 完了後にセッションデータを再読み込み
      const data = await fetchSessionData(sessionId);
      setSessionData(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to send instruction.');
    }
  };

  const handleUpdateTodo = async (sessionId: string, todos: any[]) => { // TODO: 型を定義する
    try {
      await updateTodo(sessionId, todos);
      // UIは即時更新されるため、ここでは再フェッチしない
    } catch (err: any) {
      setError(err.message || 'Failed to update todos.');
    }
  };

  const handleDeleteAllTodos = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete all todos for this session?')) return;
    try {
      await deleteTodos(sessionId);
      // セッションデータを再読み込み
      const data = await fetchSessionData(sessionId);
      setSessionData(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to delete all todos.');
    }
  };

  const handleUpdateReferencePersist = async (sessionId: string, index: number, persist: boolean) => {
    try {
      await updateReferencePersist(sessionId, index, persist);
      // UIは即時更新されるため、ここでは再フェッチしない
    } catch (err: any) {
      setError(err.message || 'Failed to update reference persist state.');
    }
  };

  const handleUpdateReferenceTtl = async (sessionId: string, index: number, ttl: number) => {
    try {
      await updateReferenceTtl(sessionId, index, ttl);
      // セッションデータを再読み込みしてUIを更新
      const data = await fetchSessionData(sessionId);
      setSessionData(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to update reference TTL.');
    }
  };

  const handleUpdateReferenceDisabled = async (sessionId: string, index: number, disabled: boolean) => {
    try {
      await updateReferenceDisabled(sessionId, index, disabled);
      // UIは即時更新されるため、ここでは再フェッチしない
    } catch (err: any) {
      setError(err.message || 'Failed to update reference disabled state.');
    }
  };

  if (loading) {
    return <div className={appContainer}>Loading...</div>;
  }

  if (error) {
    return <div className={appContainer} style={{ color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div className={appContainer}>
      <SessionList
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSessionSelect={handleSessionSelect}
      />
      <TurnsList
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        onDeleteTurn={handleDeleteTurn}
        onForkSession={handleForkSession}
        onSendInstruction={handleSendInstruction}
      />
      <SessionMeta
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        onUpdateTodo={handleUpdateTodo}
        onDeleteAllTodos={handleDeleteAllTodos}
        onUpdateReferencePersist={handleUpdateReferencePersist}
        onUpdateReferenceTtl={handleUpdateReferenceTtl}
        onUpdateReferenceDisabled={handleUpdateReferenceDisabled}
      />
    </div>
  );
};

export default HomePage;