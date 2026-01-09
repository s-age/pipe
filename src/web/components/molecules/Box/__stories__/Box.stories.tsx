import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Box } from '../index'

const Meta = {
  title: 'Molecules/Box',
  component: Box,
  tags: ['autodocs'],
  args: {
    children: 'Box Content',
    style: {
      backgroundColor: '#f0f0f0',
      minHeight: '100px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }
} satisfies StoryMeta<typeof Box>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {}
}

export const WithPadding: Story = {
  args: {
    padding: 'm'
  }
}

export const WithMargin: Story = {
  args: {
    margin: 'm',
    style: {
      backgroundColor: '#e0e0e0',
      border: '1px solid #ccc',
      minHeight: '100px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }
}

export const WithBorder: Story = {
  args: {
    border: 'thick'
  }
}

export const WithRadius: Story = {
  args: {
    radius: 'm',
    border: true
  }
}

export const CustomComponent: Story = {
  args: {
    as: 'section',
    children: 'This is a section element'
  }
}
