import React from 'react'

import { SessionControl } from '..'

export default {
  title: 'Organisms/SessionControl',
  component: SessionControl
}

export const Default = (): React.ReactElement => {
  const sessionDetail = {
    session_id: 'session_demo_001',
    purpose: 'Demo session',
    background: 'Demo background',
    roles: [],
    parent: null,
    references: [],
    artifacts: [],
    procedure: null,
    instruction: '',
    multi_step_reasoning_enabled: false,
    hyperparameters: null,
    todos: [],
    turns: []
  }

  const onRefresh = async (): Promise<void> =>
    // no-op for story
    Promise.resolve()

  return (
    <div style={{ padding: 12 }}>
      <SessionControl sessionDetail={sessionDetail} onRefresh={onRefresh} />
    </div>
  )
}
