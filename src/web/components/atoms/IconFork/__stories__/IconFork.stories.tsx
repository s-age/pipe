import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconFork } from '../index'

const Meta = {
  title: 'Atoms/IconFork',
  component: IconFork,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' }
    },
    color: {
      control: { type: 'color' }
    }
  }
} satisfies StoryMeta<typeof IconFork>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    size: 20
  }
}

export const Large: Story = {
  args: {
    size: 48,
    stroke: 'blue'
  }
}
