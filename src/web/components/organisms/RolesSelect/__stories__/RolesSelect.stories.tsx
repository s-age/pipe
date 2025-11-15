import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { RolesSelect } from '../index'

const Meta = {
  title: 'Organisms/RolesSelect',
  component: RolesSelect,
  tags: ['autodocs']
} satisfies StoryMeta<typeof RolesSelect>

export default Meta
type Story = StoryObj<typeof Meta>

const STUB_SESSION_DETAIL = {
  purpose: 'Example session',
  background: 'This is an example session for demonstration purposes.',
  roles: ['admin', 'editor'],
  artifacts: [],
  procedure: 'standard',
  references: [],
  hyperparameters: {
    temperature: 0.7,
    top_p: 0.9,
    top_k: 5
  },
  id: undefined,
  multi_step_reasoning_enabled: false,
  todos: [],
  turns: []
}

export const Default: Story = {
  args: {
    sessionDetail: STUB_SESSION_DETAIL,
    placeholder: 'Select roles'
  }
}

export const WithRHF: Story = {
  args: {
    sessionDetail: STUB_SESSION_DETAIL
  },
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <RolesSelect sessionDetail={STUB_SESSION_DETAIL} />
        <Button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </Button>
      </Form>
    )

    return <FormExample />
  }
}

export const WithoutForm: Story = {
  args: {
    sessionDetail: STUB_SESSION_DETAIL
  },
  render: (): JSX.Element => (
    <div>
      <RolesSelect sessionDetail={STUB_SESSION_DETAIL} />
    </div>
  )
}
