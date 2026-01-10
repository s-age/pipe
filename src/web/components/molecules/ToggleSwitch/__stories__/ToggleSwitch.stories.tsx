import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import type { JSX } from 'react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { ToggleSwitch } from '../index'

const Meta = {
  title: 'Molecules/ToggleSwitch',
  component: ToggleSwitch,
  tags: ['autodocs'],
  args: {
    onChange: fn()
  }
} satisfies StoryMeta<typeof ToggleSwitch>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    ariaLabel: 'Toggle switch'
  }
}

export const Checked: Story = {
  args: {
    checked: true,
    ariaLabel: 'Toggle switch checked',
    onChange: fn()
  }
}

export const Disabled: Story = {
  args: {
    disabled: true,
    ariaLabel: 'Toggle switch disabled',
    onChange: fn()
  }
}

export const WithLabel: Story = {
  args: {
    label: 'Enable notifications',
    ariaLabel: 'Toggle switch with label',
    onChange: fn()
  }
}

export const Interactive: Story = {
  render: (arguments_): JSX.Element => {
    const InteractiveExample = (): JSX.Element => {
      const [checked, setChecked] = useState(false)
      const handleChange = (value: boolean): void => {
        setChecked(value)
        arguments_.onChange?.(value)
      }

      return (
        <ToggleSwitch
          {...arguments_}
          checked={checked}
          onChange={handleChange}
          label={`Status: ${checked ? 'ON' : 'OFF'}`}
        />
      )
    }

    return <InteractiveExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const toggle = canvas.getByRole('switch')

    // Initial state
    await expect(toggle).toHaveAttribute('aria-checked', 'false')

    // Click to toggle ON
    await userEvent.click(toggle)
    await expect(toggle).toHaveAttribute('aria-checked', 'true')
    await expect(args.onChange).toHaveBeenCalledWith(true)

    // Click to toggle OFF
    await userEvent.click(toggle)
    await expect(toggle).toHaveAttribute('aria-checked', 'false')
    await expect(args.onChange).toHaveBeenCalledWith(false)
  }
}
