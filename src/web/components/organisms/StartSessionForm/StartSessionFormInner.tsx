import type { JSX } from 'react'

import { useFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'

import { useStartSessionFormHandlers } from './hooks/useStartSessionFormHandlers'
import type { StartSessionFormInputs } from './schema'
import { StartSessionContent } from './StartSessionContent'

type StartSessionFormInnerProperties = {
  sessionDetail: SessionDetail
  parentOptions: Option[]
}

export const StartSessionFormInner = ({
  sessionDetail,
  parentOptions
}: StartSessionFormInnerProperties): JSX.Element => {
  const {
    handleSubmit,
    formState: { isSubmitting }
  } = useFormContext<StartSessionFormInputs>()

  const { handleCancel, handleCreateClick } = useStartSessionFormHandlers({
    handleSubmit
  })

  return (
    <StartSessionContent
      sessionDetail={sessionDetail}
      handleCancel={handleCancel}
      handleCreateClick={handleCreateClick}
      parentOptions={parentOptions}
      isSubmitting={isSubmitting}
    />
  )
}
