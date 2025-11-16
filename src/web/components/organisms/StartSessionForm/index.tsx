import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'

export const StartSessionForm = (): JSX.Element => {
  const sessionDetail: SessionDetail = {
    session_id: null,
    purpose: '',
    background: '',
    roles: [],
    parent: null,
    references: [],
    artifacts: [],
    procedure: null,
    instruction: '',
    multi_step_reasoning_enabled: false,
    hyperparameters: null,
    todos: [],
    turns: [],
    roleOptions: undefined
  }

  return (
    <Form<StartSessionFormInputs>
      schema={formSchema}
      defaultValues={{
        session_id: '',
        background: '',
        artifacts: [],
        purpose: '',
        roles: [],
        parent: undefined,
        references: [],
        procedure: undefined,
        instruction: '',
        multi_step_reasoning_enabled: false,
        hyperparameters: null,
        todos: [],
        turns: [],
        roleOptions: undefined
      }}
    >
      <StartSessionFormInner sessionDetail={sessionDetail} />
    </Form>
  )
}
