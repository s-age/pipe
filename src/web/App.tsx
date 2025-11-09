import type { JSX } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import { ModalProvider } from '@/components/molecules/Modal/ModalProvider'

import { Toasts } from './components/organisms/Toast'
import { ChatHistoryPage } from './components/pages/ChatHistoryPage'
import { StartSessionPage } from './components/pages/StartSessionPage'
import { AppStoreProvider } from './stores/useAppStore'

export const App = (): JSX.Element => (
  <AppStoreProvider>
    <ModalProvider>
      <Router>
        <Routes>
          <Route path="/" element={<ChatHistoryPage />} />
          <Route path="/session/:sessionId" element={<ChatHistoryPage />} />
          <Route path="/start_session" element={<StartSessionPage />} />
        </Routes>
      </Router>
      <Toasts />
    </ModalProvider>
  </AppStoreProvider>
)
