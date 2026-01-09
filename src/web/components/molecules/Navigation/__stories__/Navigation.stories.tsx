import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Navigation } from '../index'

const Meta = {
  title: 'Molecules/Navigation',
  component: Navigation,
  tags: ['autodocs'],
  args: {
    children: (
      <ul>
        <li>
          <a href="#">Home</a>
        </li>
        <li>
          <a href="#">About</a>
        </li>
        <li>
          <a href="#">Contact</a>
        </li>
      </ul>
    )
  }
} satisfies StoryMeta<typeof Navigation>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    ariaLabel: 'Main Navigation'
  }
}

export const WithoutLabel: Story = {
  args: {
    ariaLabel: undefined
  }
}
