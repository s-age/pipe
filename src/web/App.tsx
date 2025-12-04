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

const SessionManagementPage = lazy(() =>
  import('./components/pages/SessionManagementPage').then((module) => ({
    default: module.SessionManagementPage
  }))
)

const router = createBrowserRouter([
  {
    path: '/',
    element: <ChatHistoryPage />
  },
  {
    path: '/session/*',
    element: <ChatHistoryPage />
  },
  {
    path: '/start_session',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <StartSessionPage />
      </Suspense>
    )
  },
  {
    path: '/session_management',
    element: (
      <Suspense fallback={<div>Loading...</div>}>
        <SessionManagementPage />
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
