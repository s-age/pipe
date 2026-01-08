import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { IconSearch } from '../index'

const Meta = {
  title: 'Atoms/IconSearch',
  component: IconSearch,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'number' }
    }
  }
} satisfies StoryMeta<typeof IconSearch>

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
    stroke: 'red'
  }
}
