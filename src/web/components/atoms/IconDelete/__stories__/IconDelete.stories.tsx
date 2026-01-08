import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { IconDelete } from '../index'

const Meta = {
  title: 'Atoms/IconDelete',
  component: IconDelete,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' },
      description: 'Icon size in pixels'
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes'
    }
  }
} satisfies StoryMeta<typeof IconDelete>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state with the standard size of 20px.
 */
export const Default: Story = {
  args: {
    size: 20
  }
}

/**
 * Large variant demonstrating the scalability of the SVG.
 */
export const Large: Story = {
  args: {
    size: 48
  }
}

/**
 * Demonstrates how the icon inherits color from its parent via `fill="currentColor"`.
 */
export const Colored: Story = {
  render: (arguments_): JSX.Element => (
    <div style={{ color: '#e53e3e' }}>
      <IconDelete {...arguments_} />
      <span style={{ marginLeft: '8px', verticalAlign: 'middle' }}>
        Inherited color
      </span>
    </div>
  ),
  args: {
    size: 24
  }
}
