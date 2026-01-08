import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { LoadingSpinner } from '../index'

const Meta = {
  title: 'Atoms/LoadingSpinner',
  component: LoadingSpinner,
  tags: ['autodocs'],
  argTypes: {
    className: { control: 'text' }
  }
} satisfies StoryMeta<typeof LoadingSpinner>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {}
}

export const WithCustomClass: Story = {
  args: {
    style: { color: 'blue', fontWeight: 'bold' }
  }
}
