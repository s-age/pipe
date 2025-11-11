import type { JSX } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import { ModalProvider } from '@/stores/useModalStore'

import { Toasts } from './components/organisms/Toast'
import { ChatHistoryPage } from './components/pages/ChatHistoryPage'
import { StartSessionPage } from './components/pages/StartSessionPage'
import { AppStoreProvider } from './stores/useAppStore'

const router = createBrowserRouter([
  {
    path: '/',
    element: <ChatHistoryPage />
  },
  {
    path: '/session/:sessionId',
    element: <ChatHistoryPage />
  },
  {
    path: '/start_session',
    element: <StartSessionPage />
  }
])

export const App = (): JSX.Element => (
  <AppStoreProvider>
    <ModalProvider>
      <RouterProvider router={router} />
      <Toasts />
    </ModalProvider>
  </AppStoreProvider>
)
