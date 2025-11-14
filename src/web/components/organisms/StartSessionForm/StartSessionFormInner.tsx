import type { JSX } from 'react'

import { useFormContext } from '@/components/organisms/Form'

import { useStartSessionFormHandlers } from './hooks/useStartSessionFormHandlers'
import type { StartSessionFormInputs } from './schema'
import { StartSessionContent } from './StartSessionContent'

export const StartSessionFormInner = (): JSX.Element => {
  const { handleSubmit } = useFormContext<StartSessionFormInputs>()

  const { handleCancel, handleCreateClick } = useStartSessionFormHandlers({
    handleSubmit
  })

  return (
    <StartSessionContent
      handleCancel={handleCancel}
      handleCreateClick={handleCreateClick}
    />
  )
}
