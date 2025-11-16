import type { JSX } from 'react'

import { useFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useStartSessionFormHandlers } from './hooks/useStartSessionFormHandlers'
import type { StartSessionFormInputs } from './schema'
import { StartSessionContent } from './StartSessionContent'

type StartSessionFormInnerProperties = {
  sessionDetail: SessionDetail
}

export const StartSessionFormInner = ({
  sessionDetail
}: StartSessionFormInnerProperties): JSX.Element => {
  const { handleSubmit } = useFormContext<StartSessionFormInputs>()

  const { handleCancel, handleCreateClick } = useStartSessionFormHandlers({
    handleSubmit
  })

  return (
    <StartSessionContent
      sessionDetail={sessionDetail}
      handleCancel={handleCancel}
      handleCreateClick={handleCreateClick}
    />
  )
}
