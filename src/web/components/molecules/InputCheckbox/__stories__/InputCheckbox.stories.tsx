import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { Form } from '@/components/organisms/Form'

import { InputCheckbox } from '../index'

const Meta = {
  title: 'Molecules/InputCheckbox',
  component: InputCheckbox,
  tags: ['autodocs'],
  args: {
    label: 'Checkbox Label',
    name: 'checkbox'
  }
} satisfies StoryMeta<typeof InputCheckbox>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state of the checkbox.
 * Demonstrates basic usage with a label and interaction.
 */
export const Default: Story = {
  args: {
    label: 'Default Checkbox'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).toBeInTheDocument()
    await expect(checkbox).not.toBeChecked()
    await userEvent.click(checkbox)
    await expect(checkbox).toBeChecked()
  }
}

/**
 * Controlled component pattern.
 * Demonstrates how to manage the checked state externally.
 */
export const Controlled: Story = {
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [checked, setChecked] = useState(false)

      return (
        <InputCheckbox
          {...arguments_}
          checked={checked}
          onChange={(event) => setChecked(event.target.checked)}
          label={`Controlled: ${checked ? 'Checked' : 'Unchecked'}`}
        />
      )
    }

    return <ControlledExample />
  }
}

/**
 * Integration with React Hook Form.
 * Demonstrates usage within a Form component.
 */
export const WithRHF: Story = {
  render: (arguments_): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <InputCheckbox {...arguments_} name="rhf-checkbox" label="RHF Integration" />
        <button type="submit" style={{ marginTop: '1rem' }}>
          Submit
        </button>
      </Form>
    )

    return <FormExample />
  }
}

/**
 * Disabled state.
 * Verifies that the checkbox is not interactive when disabled.
 */
export const Disabled: Story = {
  args: {
    label: 'Disabled Checkbox',
    disabled: true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).toBeDisabled()
  }
}
