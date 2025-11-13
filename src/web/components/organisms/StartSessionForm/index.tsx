import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'

import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'

export const StartSessionForm = (): JSX.Element => (
  <Form<StartSessionFormInputs>
    schema={formSchema}
    defaultValues={{
      background: '',
      artifacts: [],
      purpose: '',
      roles: null,
      parent: null,
      references: null,
      procedure: null,
      instruction: '',
      multi_step_reasoning_enabled: false,
      hyperparameters: null
    }}
  >
    <StartSessionFormInner />
  </Form>
)
