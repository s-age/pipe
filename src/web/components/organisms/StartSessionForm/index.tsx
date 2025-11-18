import type { JSX } from 'react'
import React from 'react'

import { Form } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'
import { wrapper } from './style.css'

type StartSessionFormProperties = {
  settings: Settings
  parentOptions: Option[]
  defaultValues?: Partial<StartSessionFormInputs> | null
}

export const StartSessionForm = ({
  settings,
  parentOptions,
  defaultValues: defaultValuesFromParent = null
}: StartSessionFormProperties): JSX.Element => {
  const computedDefaultValues = React.useMemo(() => {
    if (defaultValuesFromParent) return defaultValuesFromParent

    return {
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
    // only re-create when settings.hyperparameters changes
  }, [defaultValuesFromParent, settings.hyperparameters])

  const sessionDetail = React.useMemo(
    () => ({ ...computedDefaultValues, turns: [] }) as unknown as SessionDetail,
    [computedDefaultValues]
  )

  // `parentOptions` are normalized at the page lifecycle to avoid
  // re-computing flattening on every render of this form. Pass through
  // the already-normalized options directly to the inner form.

  return (
    <div className={wrapper}>
      <Form<StartSessionFormInputs>
        schema={formSchema}
        defaultValues={computedDefaultValues as StartSessionFormInputs}
      >
        <StartSessionFormInner
          sessionDetail={sessionDetail}
          parentOptions={parentOptions}
        />
      </Form>
    </div>
  )
}
