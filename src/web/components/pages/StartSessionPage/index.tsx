import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner'
import { AppLayout } from '@/components/layouts/AppLayout'
import { StartSessionForm } from '@/components/organisms/StartSessionForm'

import { useStartSessionPageLifecycle } from './hooks/useStartSessionPageLifecycle'
import { pageContent } from './style.css.ts'

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
      <AppLayout>
        <ErrorMessage message={error} />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className={pageContent}>
        <StartSessionForm
          settings={settings}
          parentOptions={parentOptions}
          defaultValues={startDefaults ?? undefined}
        />
      </div>
      {error && <ErrorMessage message={error} />}
    </AppLayout>
  )
}

// Default export removed — use named export `StartSessionPage`
