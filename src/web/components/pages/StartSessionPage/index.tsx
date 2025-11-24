import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner'
import { StartSessionForm } from '@/components/organisms/StartSessionForm'

import { useStartSessionPageLifecycle } from './hooks/useStartSessionPageLifecycle'
import { pageContainer, pageContent } from './style.css'

export const StartSessionPage: () => JSX.Element = () => {
  const {
    settings,
    parentOptions,
    loading,
    error: sessionDataError,
    startDefaults
  } = useStartSessionPageLifecycle()

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
      <div className={pageContent}>
        <StartSessionForm
          settings={settings}
          parentOptions={parentOptions}
          defaultValues={startDefaults ?? undefined}
        />
      </div>
      {error && <ErrorMessage message={error} />}
    </div>
  )
}

// Default export removed — use named export `StartSessionPage`
