import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner'
import { AppLayout } from '@/components/layouts/AppLayout'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { StartSessionForm } from '@/components/organisms/StartSessionForm'

import { useStartSessionPageLifecycle } from './hooks/useStartSessionPageLifecycle'
import { pageContent } from './style.css.ts'

export const StartSessionPage = (): JSX.Element => {
  const {
    error: sessionDataError,
    loading,
    parentOptions,
    settings,
    startDefaults
  } = useStartSessionPageLifecycle()

  const error = sessionDataError

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !settings) {
    return (
      <AppLayout>
        <ErrorMessage message={error || 'Failed to load settings'} />
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <FlexColumn className={pageContent}>
        <StartSessionForm
          settings={settings}
          parentOptions={parentOptions}
          defaultValues={startDefaults ?? undefined}
        />
      </FlexColumn>
    </AppLayout>
  )
}

// Default export removed — use named export `StartSessionPage`
