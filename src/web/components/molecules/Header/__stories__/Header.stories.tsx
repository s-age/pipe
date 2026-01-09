import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Header } from '../index'

const Meta = {
  title: 'Molecules/Header',
  component: Header,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof Header>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: (
      <div
        style={{
          padding: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>Logo</span>
        <nav>
          <ul
            style={{
              display: 'flex',
              gap: '1rem',
              listStyle: 'none',
              margin: 0,
              padding: 0
            }}
          >
            <li>Home</li>
            <li>About</li>
            <li>Contact</li>
          </ul>
        </nav>
      </div>
    )
  }
}

export const Sticky: Story = {
  args: {
    ...Default.args,
    sticky: true
  },
  render: (arguments_): JSX.Element => (
    <div style={{ height: '150vh', background: '#f5f5f5' }}>
      <Header {...arguments_} />
      <div style={{ padding: '2rem' }}>
        <p>Scroll down to see the sticky header in action.</p>
        {Array.from({ length: 20 }).map((_, i) => (
          <p key={i}>Content line {i + 1}</p>
        ))}
      </div>
    </div>
  )
}
