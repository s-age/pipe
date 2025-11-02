import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/pages/HomePage/index';
import NewSessionPage from './components/pages/NewSessionPage/index';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/session/:sessionId" element={<HomePage />} />
        <Route path="/new_session" element={<NewSessionPage />} />
      </Routes>
    </Router>
  );
};

export default App;
