import { expect } from '@storybook/jest'
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { userEvent, within } from '@storybook/testing-library'

import { Button } from '../index'

const Meta = {
  title: 'Atoms/Button',
  component: Button,
  tags: ['autodocs'],
  args: {
    children: 'Button Text',
    kind: 'primary',
    size: 'default',
    hasBorder: true
  },
  argTypes: {
    kind: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger']
    },
    size: {
      control: 'select',
      options: ['small', 'default', 'large', 'xsmall']
    },
    text: {
      control: 'select',
      options: ['bold', 'uppercase', undefined]
    },
    onClick: { action: 'clicked' }
  }
} satisfies StoryMeta<typeof Button>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'Primary Button'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /primary button/i })

    await expect(button).toBeTruthy()
    await userEvent.click(button)
  }
}

export const Secondary: Story = {
  args: {
    kind: 'secondary',
    children: 'Secondary Button'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /secondary button/i })

    await expect(button).toBeInTheDocument()
    await userEvent.click(button)
  }
}

export const Danger: Story = {
  args: {
    kind: 'danger',
    children: 'Danger Button'
  }
}

export const Ghost: Story = {
  args: {
    kind: 'ghost',
    children: 'Ghost Button'
  }
}

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button',
    'aria-disabled': true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /disabled button/i })

    await expect(button).toBeDisabled()
    await expect(button).toHaveAttribute('aria-disabled', 'true')
  }
}

export const Small: Story = {
  args: {
    size: 'small',
    children: 'Small Button'
  }
}

export const Large: Story = {
  args: {
    size: 'large',
    children: 'Large Button'
  }
}

export const XSmall: Story = {
  args: {
    size: 'xsmall',
    children: 'Extra Small'
  }
}

export const Bold: Story = {
  args: {
    text: 'bold',
    children: 'Bold Text'
  }
}

export const Uppercase: Story = {
  args: {
    text: 'uppercase',
    children: 'uppercase text'
  }
}

export const NoBorder: Story = {
  args: {
    hasBorder: false,
    children: 'No Border'
  }
}

export const Accessible: Story = {
  args: {
    children: 'Close',
    'aria-label': 'Close dialog'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /close dialog/i })

    await expect(button).toBeInTheDocument()
    await expect(button).toHaveAccessibleName('Close dialog')
    await userEvent.click(button)
  }
}
