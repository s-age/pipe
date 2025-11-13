import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner'
import { StartSessionForm } from '@/components/organisms/StartSessionForm'

import { useStartSessionPageLifecycle } from './hooks/useStartSessionPageLifecycle'
import { pageContainer } from './style.css'

export const StartSessionPage: () => JSX.Element = () => {
  const { loading, error: sessionDataError } = useStartSessionPageLifecycle()

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
      <StartSessionForm />
      {error && <ErrorMessage message={error} />}
    </div>
  )
}

// Default export removed — use named export `StartSessionPage`
