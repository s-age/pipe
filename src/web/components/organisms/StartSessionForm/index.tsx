import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'

type StartSessionFormProperties = {
  settings: Settings
  parentOptions: Option[]
}

export const StartSessionForm = ({
  settings,
  parentOptions
}: StartSessionFormProperties): JSX.Element => {
  const defaultValues = {
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
  }

  return (
    <Form<StartSessionFormInputs> schema={formSchema} defaultValues={defaultValues}>
      <StartSessionFormInner
        sessionDetail={{ ...defaultValues, turns: [] }}
        parentOptions={parentOptions}
      />
    </Form>
  )
}
