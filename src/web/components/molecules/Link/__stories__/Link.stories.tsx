import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, userEvent, within } from 'storybook/test'

import { Link } from '../index'

const Meta = {
  title: 'Molecules/Link',
  component: Link,
  tags: ['autodocs'],
  args: {
    href: 'https://example.com',
    children: 'Click me'
  }
} satisfies StoryMeta<typeof Link>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default link with standard behavior.
 */
export const Default: Story = {
  args: {
    children: 'Default Link'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const link = canvas.getByRole('link', { name: /default link/i })
    await expect(link).toBeInTheDocument()
    await expect(link).toHaveAttribute('href', 'https://example.com')
    await userEvent.hover(link)
  }
}

/**
 * Demonstrates different visual variants.
 */
export const Variants: Story = {
  render: (arguments_) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Link {...arguments_} variant="default">
        Default Variant
      </Link>
      <Link {...arguments_} variant="primary">
        Primary Variant
      </Link>
      <Link {...arguments_} variant="subtle">
        Subtle Variant
      </Link>
      <Link {...arguments_} variant="unstyled">
        Unstyled Variant
      </Link>
    </div>
  )
}

/**
 * External link with target="_blank" and ARIA attributes.
 */
export const External: Story = {
  args: {
    href: 'https://google.com',
    target: '_blank',
    children: 'External Link',
    'aria-label': 'Visit Google (opens in new tab)'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const link = canvas.getByRole('link', { name: /visit google/i })
    await expect(link).toBeInTheDocument()
    await expect(link).toHaveAttribute('target', '_blank')
    await expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    await expect(link).toHaveAttribute('aria-label', 'Visit Google (opens in new tab)')
    await userEvent.hover(link)
  }
}
