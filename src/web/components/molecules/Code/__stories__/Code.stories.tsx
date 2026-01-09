import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Code } from '../index'

const Meta = {
  title: 'Molecules/Code',
  component: Code,
  tags: ['autodocs'],
  argTypes: {
    block: {
      control: 'boolean'
    }
  }
} satisfies StoryMeta<typeof Code>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'npm install @pipe/core'
  }
}

export const Block: Story = {
  args: {
    block: true,
    children: `interface User {
  id: string;
  name: string;
  email: string;
}`
  }
}

export const InlineInText: Story = {
  render: (arguments_): JSX.Element => (
    <p>
      You can use <Code {...arguments_}>{arguments_.children}</Code> to highlight
      commands.
    </p>
  ),
  args: {
    children: 'git commit'
  }
}
