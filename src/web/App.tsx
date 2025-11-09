import type { JSX } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import { ChatHistoryPage as HomePage } from './components/pages/ChatHistoryPage/index'
import { StartSessionPage } from './components/pages/StartSessionPage/index'

export const App = (): JSX.Element => (
  <Router>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/session/:sessionId" element={<HomePage />} />
      <Route path="/start_session" element={<StartSessionPage />} />
    </Routes>
  </Router>
)

// Default export removed — use named export `App`
