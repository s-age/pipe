import type { JSX } from 'react'
import { Suspense, lazy } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import { ModalManager } from './components/organisms/Modal'
import { Toasts } from './components/organisms/Toast'
import { TooltipManager } from './components/organisms/Tooltip'
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
    {/* ModalProvider removed in favor of event-based ModalManager */}
    <RouterProvider router={router} />
    <Toasts />
    <ModalManager />
    <TooltipManager />
  </AppStoreProvider>
)
