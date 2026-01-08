import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconPaperPlane } from '../index'

const Meta = {
  title: 'Atoms/IconPaperPlane',
  component: IconPaperPlane,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' },
      description: 'Icon size in pixels'
    },
    color: {
      control: { type: 'color' },
      description: 'Icon stroke color'
    }
  }
} satisfies StoryMeta<typeof IconPaperPlane>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default size (24px)
 */
export const Default: Story = {
  args: {
    size: 24
  }
}

/**
 * Large size (48px)
 */
export const Large: Story = {
  args: {
    size: 48
  }
}
