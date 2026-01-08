import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconCopy } from '../index'

const Meta = {
  title: 'Atoms/IconCopy',
  component: IconCopy,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' }
    },
    className: {
      control: { type: 'text' }
    }
  }
} satisfies StoryMeta<typeof IconCopy>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    size: 20
  }
}

export const Large: Story = {
  args: {
    size: 48
  }
}

export const CustomColor: Story = {
  args: {
    size: 24,
    style: { color: 'red' }
  }
}
