import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Strong } from '../index'

const Meta = {
  title: 'Atoms/Strong',
  component: Strong,
  tags: ['autodocs'],
  args: {
    children: 'Strong text'
  }
} satisfies StoryMeta<typeof Strong>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'This is a strong text'
  }
}

export const WithLongText: Story = {
  args: {
    children:
      'This is a much longer strong text to demonstrate how it looks when it wraps or occupies more space in the layout.'
  }
}
