import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'
import { z } from 'zod'

import { Form } from '@/components/organisms/Form'

import { InputField } from '../index'

const Meta = {
  title: 'Molecules/InputField',
  component: InputField,
  tags: ['autodocs'],
  args: {
    id: 'input-field',
    label: 'Label',
    name: 'testField',
    placeholder: 'Placeholder text'
  }
} satisfies StoryMeta<typeof InputField>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: '' }}>
      <InputField {...arguments_} />
    </Form>
  )
}

export const WithError: Story = {
  render: (arguments_): JSX.Element => {
    const schema = z.object({
      [arguments_.name]: z.string().min(1, 'This field is required')
    })

    return (
      <Form schema={schema} defaultValues={{ [arguments_.name]: '' }} mode="onBlur">
        <InputField {...arguments_} />
      </Form>
    )
  },
  args: {
    label: 'Required Field',
    required: true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    // Trigger validation by typing and clearing
    await userEvent.type(input, 'test')
    await userEvent.clear(input)
    await userEvent.tab()

    const error = await canvas.findByText(/this field is required/i)
    await expect(error).toBeInTheDocument()
  }
}
