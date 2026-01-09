import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Main } from '../index'

const Meta = {
  title: 'Molecules/Main',
  component: Main,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof Main>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'Main content goes here',
    style: { padding: '20px' }
  }
}

export const WithChildren: Story = {
  render: (arguments_): JSX.Element => (
    <Main {...arguments_}>
      <div
        style={{
          padding: '2rem',
          backgroundColor: '#f0f0f0',
          border: '1px dashed #ccc',
          textAlign: 'center'
        }}
      >
        <h2>Section Title</h2>
        <p>This is a demonstration of the Main component wrapping other elements.</p>
      </div>
    </Main>
  )
}
