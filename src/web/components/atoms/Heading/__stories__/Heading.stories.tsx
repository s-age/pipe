import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Heading } from '../index'

const Meta = {
  title: 'Atoms/Heading',
  component: Heading,
  tags: ['autodocs'],
  args: {
    children: 'Heading Text'
  }
} satisfies StoryMeta<typeof Heading>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default heading (Level 1)
 */
export const Default: Story = {
  args: {
    level: 1,
    children: 'Level 1 Heading (Default)'
  }
}

/**
 * Demonstration of all heading levels
 */
export const AllLevels: Story = {
  render: (): JSX.Element => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Heading level={1}>Level 1 Heading</Heading>
      <Heading level={2}>Level 2 Heading</Heading>
      <Heading level={3}>Level 3 Heading</Heading>
      <Heading level={4}>Level 4 Heading</Heading>
      <Heading level={5}>Level 5 Heading</Heading>
      <Heading level={6}>Level 6 Heading</Heading>
    </div>
  )
}
