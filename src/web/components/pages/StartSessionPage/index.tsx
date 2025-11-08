import type { JSX } from 'react'

import ErrorMessage from '@/components/atoms/ErrorMessage'
import LoadingSpinner from '@/components/atoms/LoadingSpinner'
import StartSessionForm from '@/components/organisms/StartSessionForm'
import { useSessionCreation } from '@/components/pages/StartSessionPage/hooks/useSessionCreation'

import { useStartSessionData } from './hooks/useStartSessionData'
import { pageContainer } from './style.css'

const StartSessionPage: () => JSX.Element = () => {
  const {
    sessionTree,
    settings,
    loading,
    error: sessionDataError,
  } = useStartSessionData()
  const { handleSubmit, error: sessionCreationError } = useSessionCreation()

  const error = sessionDataError || sessionCreationError

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

export default StartSessionPage
