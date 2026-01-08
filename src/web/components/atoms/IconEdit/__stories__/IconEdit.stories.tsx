import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconEdit } from '../index'

const Meta = {
  title: 'Atoms/IconEdit',
  component: IconEdit,
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
} satisfies StoryMeta<typeof IconEdit>

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
    size: 32,
    style: { stroke: 'red' }
  }
}
