import type { JSX } from 'react'

import { Box } from '@/components/molecules/Box'
import { Form } from '@/components/organisms/Form'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

import { useStartSessionFormLifecycle } from './hooks/useStartSessionFormLifecycle'
import { formSchema, type StartSessionFormInputs } from './schema'
import { StartSessionFormInner } from './StartSessionFormInner'
import { wrapper } from './style.css'

type StartSessionFormProperties = {
  parentOptions: Option[]
  settings: Settings
  defaultValues?: Partial<StartSessionFormInputs> | null
}

export const StartSessionForm = ({
  parentOptions,
  settings,
  defaultValues: defaultValuesFromParent = null
}: StartSessionFormProperties): JSX.Element => {
  const { computedDefaultValues, sessionDetail } = useStartSessionFormLifecycle({
    settings,
    defaultValuesFromParent
  })

  // `parentOptions` are normalized at the page lifecycle to avoid
  // re-computing flattening on every render of this form. Pass through
  // the already-normalized options directly to the inner form.

  return (
    <Box className={wrapper}>
      <Form<StartSessionFormInputs>
        schema={formSchema}
        defaultValues={computedDefaultValues as StartSessionFormInputs}
      >
        <StartSessionFormInner
          sessionDetail={sessionDetail}
          parentOptions={parentOptions}
        />
      </Form>
    </Box>
  )
}
