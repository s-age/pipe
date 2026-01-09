import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'
import { z } from 'zod'

import { Form } from '@/components/organisms/Form'

import { SelectField } from '../index'

const Meta = {
  title: 'Molecules/SelectField',
  component: SelectField,
  tags: ['autodocs'],
  args: {
    id: 'select-field',
    label: 'Select Option',
    name: 'selectField',
    options: [
      { label: 'Option 1', value: '1' },
      { label: 'Option 2', value: '2' },
      { label: 'Option 3', value: '3' }
    ]
  }
} satisfies StoryMeta<typeof SelectField>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: '' }}>
      <SelectField {...arguments_} />
    </Form>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const label = canvas.getByText(/select option/i)
    await expect(label).toBeInTheDocument()

    const select = canvas.getByRole('combobox')
    await expect(select).toBeInTheDocument()

    await userEvent.selectOptions(select, '2')
    await expect(select).toHaveValue('2')
  }
}

export const WithError: Story = {
  render: (arguments_): JSX.Element => {
    const schema = z.object({
      [arguments_.name]: z.string().min(1, 'Selection is required')
    })

    return (
      <Form schema={schema} defaultValues={{ [arguments_.name]: '' }} mode="onBlur">
        <SelectField {...arguments_} />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const select = canvas.getByRole('combobox')

    // Trigger validation by focusing and blurring
    await userEvent.click(select)
    await userEvent.tab()

    const error = await canvas.findByText(/selection is required/i)
    await expect(error).toBeInTheDocument()
  }
}

export const Disabled: Story = {
  args: {
    disabled: true
  },
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ [arguments_.name]: '' }}>
      <SelectField {...arguments_} />
    </Form>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const select = canvas.getByRole('combobox')
    await expect(select).toBeDisabled()
  }
}
