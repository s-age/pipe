import type { JSX } from 'react'
import React from 'react'

import { Form } from '@/components/organisms/Form'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'
import { wrapper } from './style.css'

type StartSessionFormProperties = {
  settings: Settings
  parentOptions: Option[]
}

export const StartSessionForm = ({
  settings,
  parentOptions
}: StartSessionFormProperties): JSX.Element => {
  const defaultValues = React.useMemo(
    () => ({
      session_id: '',
      purpose: '',
      background: '',
      roles: [],
      parent: null,
      references: [],
      artifacts: [],
      procedure: null,
      instruction: '',
      multi_step_reasoning_enabled: false,
      hyperparameters: settings.hyperparameters,
      todos: []
    }),
    [settings.hyperparameters]
  )

  const sessionDetail = React.useMemo(
    () => ({ ...defaultValues, turns: [] }),
    [defaultValues]
  )

  return (
    <div className={wrapper}>
      <Form<StartSessionFormInputs> schema={formSchema} defaultValues={defaultValues}>
        <StartSessionFormInner
          sessionDetail={sessionDetail}
          parentOptions={parentOptions}
        />
      </Form>
    </div>
  )
}
