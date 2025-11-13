import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Form } from '@/components/organisms/Form'

import { RolesSelect } from '../index'

const Meta = {
  title: 'Molecules/RolesSelect',
  component: RolesSelect,
  tags: ['autodocs']
} satisfies StoryMeta<typeof RolesSelect>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Select roles'
  }
}

export const WithRHF: Story = {
  args: {},
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <RolesSelect />
        <Button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </Button>
      </Form>
    )

    return <FormExample />
  }
}

export const WithoutForm: Story = {
  args: {},
  render: (): JSX.Element => (
    <div>
      <RolesSelect />
    </div>
  )
}
