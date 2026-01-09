import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Aside } from '../index'

const Meta = {
  title: 'Molecules/Aside',
  component: Aside,
  tags: ['autodocs'],
  argTypes: {
    position: {
      control: 'select',
      options: ['left', 'right', undefined]
    }
  }
} satisfies StoryMeta<typeof Aside>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: (
      <div style={{ padding: '20px', background: '#f0f0f0' }}>
        Aside Content (Default)
      </div>
    )
  }
}

export const Left: Story = {
  args: {
    position: 'left',
    children: (
      <div style={{ padding: '20px', background: '#e0f7fa' }}>
        Aside Content (Left Position)
      </div>
    )
  }
}

export const Right: Story = {
  args: {
    position: 'right',
    children: (
      <div style={{ padding: '20px', background: '#fce4ec' }}>
        Aside Content (Right Position)
      </div>
    )
  }
}
