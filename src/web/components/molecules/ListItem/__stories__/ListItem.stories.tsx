import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, within } from 'storybook/test'

import { ListItem } from '../index'

const Meta = {
  title: 'Molecules/ListItem',
  component: ListItem,
  tags: ['autodocs'],
  argTypes: {
    padding: {
      control: 'select',
      options: ['s', 'm', 'l', 'none']
    }
  }
} satisfies StoryMeta<typeof ListItem>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'List Item Content',
    padding: 'none'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const item = canvas.getByRole('listitem')
    await expect(item).toBeInTheDocument()
    await expect(item).toHaveTextContent('List Item Content')
  }
}

export const PaddingSmall: Story = {
  args: {
    children: 'Small Padding Item',
    padding: 's'
  }
}

export const PaddingMedium: Story = {
  args: {
    children: 'Medium Padding Item',
    padding: 'm'
  }
}

export const PaddingLarge: Story = {
  args: {
    children: 'Large Padding Item',
    padding: 'l'
  }
}

export const InList: Story = {
  render: (arguments_): JSX.Element => (
    <ul style={{ listStyle: 'none', padding: 0, border: '1px solid #eee' }}>
      <ListItem {...arguments_}>First Item</ListItem>
      <ListItem {...arguments_}>Second Item</ListItem>
      <ListItem {...arguments_}>Third Item</ListItem>
    </ul>
  ),
  args: {
    padding: 'm'
  }
}
