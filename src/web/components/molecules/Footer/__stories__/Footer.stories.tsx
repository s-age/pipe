import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Footer } from '../index'

const Meta = {
  title: 'Molecules/Footer',
  component: Footer,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof Footer>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: (
      <div style={{ padding: '1rem', textAlign: 'center' }}>
        © 2024 My Application. All rights reserved.
      </div>
    )
  }
}

export const Sticky: Story = {
  args: {
    sticky: true,
    children: (
      <div style={{ padding: '1rem', textAlign: 'center' }}>Sticky Footer Content</div>
    )
  },
  render: (arguments_): JSX.Element => (
    <div style={{ height: '150vh', position: 'relative' }}>
      <div style={{ padding: '1rem' }}>Scroll down to see the sticky footer.</div>
      <Footer {...arguments_} />
    </div>
  )
}
