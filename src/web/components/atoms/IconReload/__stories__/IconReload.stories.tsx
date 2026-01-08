import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconReload } from '../index'

const Meta = {
  title: 'Atoms/IconReload',
  component: IconReload,
  tags: ['autodocs'],
  args: {
    size: 20
  }
} satisfies StoryMeta<typeof IconReload>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default reload icon with standard size (20px).
 */
export const Default: Story = {
  args: {
    'aria-label': 'Reload'
  }
}

/**
 * Large reload icon (40px) to demonstrate size scaling.
 */
export const Large: Story = {
  args: {
    size: 40,
    'aria-label': 'Large reload'
  }
}
