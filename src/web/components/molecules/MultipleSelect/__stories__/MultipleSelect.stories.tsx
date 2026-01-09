import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'
import { z } from 'zod'

import { Form } from '@/components/organisms/Form'

import { MultipleSelect } from '../index'

const Meta = {
  title: 'Molecules/MultipleSelect',
  component: MultipleSelect,
  tags: ['autodocs'],
  args: {
    name: 'multiple-select',
    options: [
      { value: 'apple', label: 'Apple' },
      { value: 'banana', label: 'Banana' },
      { value: 'cherry', label: 'Cherry' },
      { value: 'date', label: 'Date' },
      { value: 'elderberry', label: 'Elderberry' }
    ],
    placeholder: 'Select fruits...'
  }
} satisfies StoryMeta<typeof MultipleSelect>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {}
}

export const Searchable: Story = {
  args: {
    searchable: true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /select fruits/i })

    await expect(trigger).toBeInTheDocument()
    await userEvent.click(trigger)

    const searchInput = canvas.getByRole('textbox', { name: /search options/i })
    await expect(searchInput).toBeInTheDocument()

    await userEvent.type(searchInput, 'apple')
    const option = canvas.getByRole('option', { name: /apple/i })
    await expect(option).toBeInTheDocument()
  }
}

export const WithDefaultValues: Story = {
  args: {
    defaultValue: ['apple', 'cherry']
  }
}

export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const schema = z.object({
      [arguments_.name]: z.array(z.string()).min(1, 'Please select at least one fruit')
    })

    return (
      <Form schema={schema} defaultValues={{ [arguments_.name]: [] }} mode="onBlur">
        <div style={{ display: 'grid', gap: '1rem' }}>
          <MultipleSelect {...arguments_} />
          <button type="submit">Submit</button>
        </div>
      </Form>
    )
  }
}

export const Disabled: Story = {
  args: {
    disabled: true
  }
}
