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

export const CloseAndClearHighlight: Story = {
  args: {
    searchable: false
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')

    await userEvent.click(trigger)
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    const firstOption = canvas.getByRole('option', { name: /apple/i })
    await userEvent.click(firstOption)

    // MultipleSelect doesn't close on option click, toggle the trigger to close
    await userEvent.click(trigger)

    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()
  }
}

/**
 * Tests outside click behavior to trigger close and clearHighlight (lines 87-88).
 */
export const OutsideClick: Story = {
  args: {
    searchable: true
  },
  render: (arguments_): JSX.Element => (
    <div>
      <div
        id="outside-element"
        style={{ marginBottom: '1rem', padding: '1rem', background: '#f0f0f0' }}
      >
        Click here after opening the select
      </div>
      <MultipleSelect {...arguments_} />
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')

    // Open the select
    await userEvent.click(trigger)
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    // Hover to highlight an option
    const firstOption = canvas.getByRole('option', { name: /apple/i })
    await userEvent.hover(firstOption)

    // Click outside to trigger close and clearHighlight
    const outsideElement = canvas.getByText(/click here after opening/i)
    await userEvent.click(outsideElement)

    // Verify listbox is closed
    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()
  }
}

/**
 * Tests with no options provided (line 58 coverage).
 */
export const NoOptions: Story = {
  args: {
    name: 'no-options',
    options: undefined
  }
}

/**
 * Tests with no placeholder provided (line 151 coverage).
 */
export const NoPlaceholder: Story = {
  args: {
    name: 'no-placeholder',
    placeholder: undefined,
    options: ['Option 1', 'Option 2']
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /select options/i })
    await expect(trigger).toBeInTheDocument()
  }
}

/**
 * Tests with options containing non-string labels (lines 112-114 coverage).
 */
export const NonStringLabels: Story = {
  args: {
    name: 'non-string-labels',
    options: [
      { value: '1', label: 123 as unknown as string },
      { value: '2', label: true as unknown as string }
    ]
  }
}

/**
 * Tests options with duplicate values to cover key generation (line 194 coverage).
 */
export const DuplicateValues: Story = {
  args: {
    name: 'duplicate-values',
    options: [
      { value: 'same', label: 'First' },
      { value: 'same', label: 'Second' },
      { value: '', label: 'Empty Value' }
    ]
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const options = within(listbox).getAllByRole('option')
    await expect(options).toHaveLength(3)
  }
}
