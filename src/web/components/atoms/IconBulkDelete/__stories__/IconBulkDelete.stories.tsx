import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconBulkDelete } from '../index'

const Meta = {
  title: 'Atoms/IconBulkDelete',
  component: IconBulkDelete,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' },
      description: 'Icon size in pixels'
    }
  }
} satisfies StoryMeta<typeof IconBulkDelete>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default icon size (20px).
 */
export const Default: Story = {
  args: {
    size: 20
  }
}

/**
 * Larger icon size (48px) to demonstrate scalability.
 */
export const Large: Story = {
  args: {
    size: 48
  }
}

/**
 * Custom color applied via style prop.
 */
export const Colored: Story = {
  args: {
    size: 24,
    style: { color: '#ff4d4f' }
  }
}
