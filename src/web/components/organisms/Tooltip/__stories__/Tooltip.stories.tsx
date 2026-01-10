import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { Tooltip, TooltipManager } from '../index'

const Meta = {
  title: 'Organisms/Tooltip',
  component: Tooltip,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <div
        style={{
          padding: '100px',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '200px'
        }}
      >
        <TooltipManager />
        <Story />
      </div>
    )
  ]
} satisfies StoryMeta<typeof Tooltip>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default tooltip appearing at the top.
 */
export const Default: Story = {
  args: {
    children: <button type="button">Hover me (Top)</button>,
    content: 'This is a top tooltip',
    placement: 'top'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /hover me/i })

    await userEvent.hover(trigger)

    // Tooltip is in a portal, so we search in document.body
    const body = within(document.body)
    const tooltip = await body.findByRole('tooltip')
    await expect(tooltip).toBeInTheDocument()
    await expect(tooltip).toHaveTextContent('This is a top tooltip')

    await userEvent.unhover(trigger)
    // The tooltip should be removed from DOM when not active
    await expect(tooltip).not.toBeInTheDocument()
  }
}

/**
 * Tooltip appearing at the bottom.
 */
export const Bottom: Story = {
  args: {
    children: <button type="button">Hover me (Bottom)</button>,
    content: 'This is a bottom tooltip',
    placement: 'bottom'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /hover me/i })

    await userEvent.hover(trigger)

    const body = within(document.body)
    const tooltip = await body.findByRole('tooltip')
    await expect(tooltip).toBeInTheDocument()
    await expect(tooltip).toHaveTextContent('This is a bottom tooltip')

    await userEvent.unhover(trigger)
  }
}

/**
 * Tooltip appearing on the left.
 */
export const Left: Story = {
  args: {
    children: <button type="button">Hover me (Left)</button>,
    content: 'This is a left tooltip',
    placement: 'left'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /hover me/i })

    await userEvent.hover(trigger)

    const body = within(document.body)
    const tooltip = await body.findByRole('tooltip')
    await expect(tooltip).toBeInTheDocument()
    await expect(tooltip).toHaveTextContent('This is a left tooltip')

    await userEvent.unhover(trigger)
  }
}

/**
 * Tooltip appearing on the right.
 */
export const Right: Story = {
  args: {
    children: <button type="button">Hover me (Right)</button>,
    content: 'This is a right tooltip',
    placement: 'right'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /hover me/i })

    await userEvent.hover(trigger)

    const body = within(document.body)
    const tooltip = await body.findByRole('tooltip')
    await expect(tooltip).toBeInTheDocument()
    await expect(tooltip).toHaveTextContent('This is a right tooltip')

    await userEvent.unhover(trigger)
  }
}
