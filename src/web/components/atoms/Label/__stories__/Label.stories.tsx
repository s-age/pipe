import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Label } from '../index'

const Meta = {
  title: 'Atoms/Label',
  component: Label,
  tags: ['autodocs'],
  args: {
    children: 'Label Text'
  }
} satisfies StoryMeta<typeof Label>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'Default Label'
  }
}

export const Required: Story = {
  args: {
    children: 'Required Field',
    required: true
  }
}
