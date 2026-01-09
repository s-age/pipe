import { expect } from '@storybook/jest'
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { userEvent, within } from '@storybook/testing-library'
import type { JSX } from 'react'
import { useState } from 'react'

import { Accordion } from '../index'

const Meta = {
  title: 'Molecules/Accordion',
  component: Accordion,
  tags: ['autodocs'],
  args: {
    title: 'Accordion Title',
    children: 'This is the accordion content. It can contain any React nodes.'
  }
} satisfies StoryMeta<typeof Accordion>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state of the Accordion, initially closed.
 */
export const Default: Story = {
  args: {
    defaultOpen: false
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const header = canvas.getByRole('button', { name: /accordion title/i })

    // Initially closed
    await expect(header).toHaveAttribute('aria-expanded', 'false')
    await expect(canvas.queryByRole('region')).not.toBeInTheDocument()

    // Click to open
    await userEvent.click(header)
    await expect(header).toHaveAttribute('aria-expanded', 'true')
    await expect(canvas.getByRole('region')).toBeInTheDocument()
  }
}

/**
 * Accordion that is open by default.
 */
export const DefaultOpen: Story = {
  args: {
    defaultOpen: true,
    title: 'Initially Open Accordion'
  }
}

/**
 * Accordion demonstrating the summary prop, which appears next to the title.
 */
export const WithSummary: Story = {
  args: {
    title: 'Accordion with Summary',
    summary: 'This is a brief summary shown in the header'
  }
}

/**
 * Controlled Accordion where the open state is managed by the parent component.
 */
export const Controlled: Story = {
  render: (arguments_): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [open, setOpen] = useState(false)

      return (
        <Accordion
          {...arguments_}
          open={open}
          onOpenChange={setOpen}
          title={`Controlled Accordion (State: ${open ? 'Open' : 'Closed'})`}
        >
          Controlled content
        </Accordion>
      )
    }

    return <ControlledExample />
  }
}
