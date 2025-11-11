import type { Meta, StoryObj } from '@storybook/react-vite'

import { ToggleSwitch } from './index'

const meta: Meta<typeof ToggleSwitch> = {
  title: 'Molecules/ToggleSwitch',
  component: ToggleSwitch,
  parameters: {
    layout: 'centered'
  },
  tags: ['autodocs'],
  argTypes: {
    checked: {
      control: 'boolean',
      description: 'Whether the switch is checked'
    },
    onChange: {
      action: 'changed',
      description: 'Callback when the switch state changes'
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the switch is disabled'
    },
    label: {
      control: 'text',
      description: 'Optional label text'
    },
    ariaLabel: {
      control: 'text',
      description: 'Accessibility label'
    }
  }
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    checked: false,
    onChange: (checked: boolean) => console.log('Toggled:', checked)
  }
}

export const Checked: Story = {
  args: {
    checked: true,
    onChange: (checked: boolean) => console.log('Toggled:', checked)
  }
}

export const Disabled: Story = {
  args: {
    checked: false,
    disabled: true,
    onChange: (checked: boolean) => console.log('Toggled:', checked)
  }
}

export const WithLabel: Story = {
  args: {
    checked: false,
    label: 'Enable notifications',
    onChange: (checked: boolean) => console.log('Toggled:', checked)
  }
}

export const CheckedWithLabel: Story = {
  args: {
    checked: true,
    label: 'Dark mode',
    onChange: (checked: boolean) => console.log('Toggled:', checked)
  }
}
