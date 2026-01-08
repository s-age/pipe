import { expect } from '@storybook/jest'
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { userEvent, within } from '@storybook/testing-library'

import { Checkbox } from '../index'

const Meta = {
  title: 'Atoms/Checkbox',
  component: Checkbox,
  tags: ['autodocs'],
  args: {
    'aria-label': 'Checkbox label'
  }
} satisfies StoryMeta<typeof Checkbox>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state of the checkbox (unchecked).
 */
export const Default: Story = {
  args: {
    defaultChecked: false
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).not.toBeChecked()
  }
}

/**
 * Checked state of the checkbox.
 */
export const Checked: Story = {
  args: {
    defaultChecked: true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).toBeChecked()
  }
}

/**
 * Disabled state of the checkbox.
 */
export const Disabled: Story = {
  args: {
    disabled: true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).toBeDisabled()
  }
}

/**
 * Demonstrates user interaction with the checkbox.
 */
export const Interaction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')

    // Initial state
    await expect(checkbox).not.toBeChecked()

    // Click to check
    await userEvent.click(checkbox)
    await expect(checkbox).toBeChecked()

    // Click to uncheck
    await userEvent.click(checkbox)
    await expect(checkbox).not.toBeChecked()
  }
}
