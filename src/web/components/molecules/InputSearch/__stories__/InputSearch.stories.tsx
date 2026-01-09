import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState, type JSX } from 'react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { Form } from '@/components/organisms/Form'

import { InputSearch } from '../index'

const Meta = {
  title: 'Molecules/InputSearch',
  component: InputSearch,
  tags: ['autodocs'],
  args: {
    onChange: fn(),
    onSubmit: fn()
  }
} satisfies StoryMeta<typeof InputSearch>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default search input with standard placeholder.
 */
export const Default: Story = {
  args: {
    placeholder: 'Search...'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /search/i })
    await expect(input).toBeInTheDocument()
    await expect(input).toHaveAttribute('placeholder', 'Search...')
  }
}

/**
 * Controlled component example showing state management.
 */
export const Controlled: Story = {
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState('')

      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <InputSearch
            {...arguments_}
            value={value}
            onChange={(v) => {
              setValue(v)
              arguments_.onChange?.(v)
            }}
          />
          <div style={{ fontSize: '14px', color: '#666' }}>
            Current value: <strong>{value}</strong>
          </div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /search/i })
    await userEvent.type(input, 'hello world')
    await expect(input).toHaveValue('hello world')
    await expect(args.onChange).toHaveBeenCalled()
  }
}

/**
 * Integration with React Hook Form using the Form organism.
 * Note: InputSearch has its own form element, so we register it with Form context.
 */
export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <div>
        <Form>
          <div style={{ marginBottom: '16px' }}>
            <label>Other form field:</label>
            <input name="otherField" placeholder="Other field" />
          </div>
        </Form>
        <InputSearch {...arguments_} name="searchQuery" />
      </div>
    )

    return <FormExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /search/i })
    await userEvent.type(input, 'rhf search')
    await expect(input).toHaveValue('rhf search')

    const submitButton = canvas.getByRole('button', { name: /search/i })
    await userEvent.click(submitButton)
    await expect(args.onSubmit).toHaveBeenCalled()
  }
}

/**
 * Search input with a custom placeholder text.
 */
export const CustomPlaceholder: Story = {
  args: {
    placeholder: 'Find users by name...'
  }
}

/**
 * Demonstrates the submit interaction.
 */
export const SubmitInteraction: Story = {
  args: {
    onSubmit: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /search/i })
    const button = canvas.getByRole('button', { name: /search/i })

    await userEvent.type(input, 'search term')
    await userEvent.click(button)

    await expect(args.onSubmit).toHaveBeenCalled()
  }
}
