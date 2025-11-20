import React from 'react'

import { Compressor } from '../index'

export default {
  title: 'Components/Compressor',
  component: Compressor
}

export const Default = (): React.ReactElement => (
  <div style={{ padding: 16 }}>
    <Compressor sessionId="session_abc123" mockMaxTurn={8} />
  </div>
)
