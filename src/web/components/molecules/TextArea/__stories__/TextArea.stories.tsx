import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import type { JSX } from 'react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { Form } from '@/components/organisms/Form'

import { TextArea } from '../index'

const Meta = {
  title: 'Molecules/TextArea',
  component: TextArea,
  tags: ['autodocs'],
  args: {
    onChange: fn()
  }
} satisfies StoryMeta<typeof TextArea>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Write something…',
    name: 'notes',
    rows: 4,
    'aria-label': 'Notes'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox', { name: /notes/i })

    await expect(textarea).toBeInTheDocument()
    await userEvent.type(textarea, 'Hello World')
    await expect(textarea).toHaveValue('Hello World')
  }
}

export const Controlled: Story = {
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState('initial text')

      const handleChange = (v: string): void => {
        setValue(v)
        arguments_.onChange?.(v)
      }

      return (
        <div>
          <TextArea
            {...arguments_}
            value={value}
            onChange={handleChange}
            rows={6}
            aria-label="Controlled textarea"
          />
          <div style={{ marginTop: 8 }}>Current: {value}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox', { name: /controlled textarea/i })

    await userEvent.clear(textarea)
    await userEvent.type(textarea, 'Updated text')
    await expect(textarea).toHaveValue('Updated text')
    await expect(canvas.getByText(/current: updated text/i)).toBeInTheDocument()
    await expect(args.onChange).toHaveBeenCalled()
  }
}

export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <TextArea
          {...arguments_}
          name="comments"
          rows={4}
          aria-label="Comments"
          aria-required={true}
        />
        <button type="submit">Submit</button>
      </Form>
    )

    return <FormExample />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox', { name: /comments/i })

    await userEvent.type(textarea, 'RHF test content')
    await expect(textarea).toHaveValue('RHF test content')
  }
}

export const Disabled: Story = {
  args: {
    disabled: true,
    value: 'This is disabled',
    'aria-label': 'Disabled textarea'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox', { name: /disabled textarea/i })

    await expect(textarea).toBeDisabled()
  }
}

export const WithError: Story = {
  args: {
    'aria-invalid': true,
    'aria-label': 'Error textarea',
    placeholder: 'Has error state'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const textarea = canvas.getByRole('textbox', { name: /error textarea/i })

    await expect(textarea).toHaveAttribute('aria-invalid', 'true')
  }
}
