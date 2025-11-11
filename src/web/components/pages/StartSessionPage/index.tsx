import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner'
import { StartSessionForm } from '@/components/organisms/StartSessionForm'

import { useStartSessionPageHandlers } from './hooks/useStartSessionPageHandlers'
import { useStartSessionPageLifecycle } from './hooks/useStartSessionPageLifecycle'
import { pageContainer } from './style.css'

export const StartSessionPage: () => JSX.Element = () => {
  const {
    sessionTree,
    settings,
    loading,
    error: sessionDataError
  } = useStartSessionPageLifecycle()
  const { handleSubmit } = useStartSessionPageHandlers()

  const error = sessionDataError

  if (loading) {
    return <LoadingSpinner />
  }

  if (error && !loading) {
    return (
      <div className={pageContainer}>
        <ErrorMessage message={error} />
      </div>
    )
  }

  return (
    <div className={pageContainer}>
      <StartSessionForm
        onSubmit={handleSubmit}
        sessions={sessionTree}
        defaultSettings={settings}
      />
      {error && <ErrorMessage message={error} />}
    </div>
  )
}

// Default export removed — use named export `StartSessionPage`
