import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import HomePage from './components/pages/HomePage/index'
import StartSessionPage from './components/pages/StartSessionPage/index'

const App: React.FC = () => (
  <Router>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/session/:sessionId" element={<HomePage />} />
      <Route path="/start_session" element={<StartSessionPage />} />
    </Routes>
  </Router>
)

export default App
