import React, { useState, useEffect } from 'react';
import NewSessionForm from '@/components/organisms/NewSessionForm';
import { createSession, fetchSessions, fetchSettings } from '@/lib/api_client/client';
import { pageContainer, errorMessageStyle } from './style.css';

interface SessionOption {
  value: string;
  label: string;
}

const NewSessionPage: React.FC = () => {
  const [sessions, setSessions] = useState<SessionOption[]>([]);
  const [settings, setSettings] = useState<any>(null); // TODO: 型を定義する
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sessionsData, settingsData] = await Promise.all([
          fetchSessions(),
          fetchSettings(),
        ]);
        setSessions(sessionsData.map((s: any) => ({ value: s[0], label: s[1].purpose })));
        setSettings(settingsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load initial data.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleSubmit = async (data: any) => { // TODO: 型を定義する
    setError(null);
    try {
      const result = await createSession(data);
      if (result.success) {
        window.location.href = `/session/${result.session_id}`;
      } else {
        setError(result.message || 'Failed to create session.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during session creation.');
    }
  };

  if (loading) {
    return <div className={pageContainer}>Loading...</div>;
  }

  if (error && !loading) {
    return <div className={pageContainer}><p className={errorMessageStyle}>{error}</p></div>;
  }

  return (
    <div className={pageContainer}>
      <NewSessionForm onSubmit={handleSubmit} sessions={sessions} defaultSettings={settings} />
      {error && <p className={errorMessageStyle}>{error}</p>}
    </div>
  );
};

export default NewSessionPage;