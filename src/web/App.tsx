import type { JSX } from 'react'
import { Suspense, lazy } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import { ModalProvider } from '@/stores/useModalStore'

import { Toasts } from './components/organisms/Toast'
import { ChatHistoryPage } from './components/pages/ChatHistoryPage'
import { AppStoreProvider } from './stores/useAppStore'

const StartSessionPage = lazy(() =>
  import('./components/pages/StartSessionPage').then((module) => ({
    default: module.StartSessionPage
  }))
)

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
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <StartSessionPage />
      </Suspense>
    )
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
