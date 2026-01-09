import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Article } from '../index'

const Meta = {
  title: 'Molecules/Article',
  component: Article,
  tags: ['autodocs'],
  args: {
    children: (
      <div>
        <h2>Article Title</h2>
        <p>
          This is a sample article content to demonstrate the Article component and its
          padding variants.
        </p>
      </div>
    )
  }
} satisfies StoryMeta<typeof Article>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    padding: 'none'
  }
}

export const PaddingSmall: Story = {
  args: {
    padding: 's'
  }
}

export const PaddingMedium: Story = {
  args: {
    padding: 'm'
  }
}

export const PaddingLarge: Story = {
  args: {
    padding: 'l'
  }
}

export const WithCustomClassName: Story = {
  args: {
    padding: 'm',
    style: { border: '1px solid #ccc', borderRadius: '8px' }
  }
}
