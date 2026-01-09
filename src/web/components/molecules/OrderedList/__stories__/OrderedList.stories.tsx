import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { OrderedList } from '../index'

const Meta = {
  title: 'Molecules/OrderedList',
  component: OrderedList,
  tags: ['autodocs'],
  args: {
    children: (
      <>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
      </>
    )
  }
} satisfies StoryMeta<typeof OrderedList>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    type: '1',
    gap: 'none'
  }
}

export const WithGap: Story = {
  args: {
    gap: 'm'
  }
}

export const AlphaType: Story = {
  args: {
    type: 'a'
  }
}

export const RomanType: Story = {
  args: {
    type: 'I'
  }
}

export const CustomClassName: Story = {
  render: (arguments_): JSX.Element => (
    <div style={{ padding: '1rem', backgroundColor: '#f0f0f0' }}>
      <OrderedList {...arguments_} />
    </div>
  ),
  args: {
    gap: 's'
  }
}
