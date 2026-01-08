import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Emphasis } from '../index'

const Meta = {
  title: 'Atoms/Emphasis',
  component: Emphasis,
  tags: ['autodocs']
} satisfies StoryMeta<typeof Emphasis>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'This text is emphasized'
  }
}

export const LongText: Story = {
  args: {
    children:
      'This is a much longer piece of text that is being emphasized to see how it wraps and looks in a block context.'
  }
}
