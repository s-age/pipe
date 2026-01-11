import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'
import { z } from 'zod'

import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { ReferenceList } from '../index'

const Meta = {
  title: 'Organisms/ReferenceList',
  component: ReferenceList,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <div
          style={{ padding: '20px', backgroundColor: '#1e1e1e', minHeight: '400px' }}
        >
          <Story />
        </div>
      </AppStoreProvider>
    )
  ],
  args: {
    refreshSessions: fn()
  }
} satisfies StoryMeta<typeof ReferenceList>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state with existing references.
 */
export const Default: Story = {
  args: {
    sessionDetail: {
      sessionId: 'session-123',
      references: [
        {
          path: 'src/web/components/organisms/ReferenceList/index.tsx',
          disabled: false,
          ttl: 3,
          persist: false
        },
        {
          path: 'src/web/components/organisms/ReferenceList/style.css.ts',
          disabled: true,
          ttl: 5,
          persist: true
        }
      ]
    } as unknown as SessionDetail
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify label
    await expect(canvas.getByText(/References:/i)).toBeInTheDocument()

    // Verify summary text
    await expect(canvas.getByText(/2 references/i)).toBeInTheDocument()

    // Find the accordion header and open it if closed
    const accordionHeader = canvas.getByRole('button', {
      name: /advanced settings/i
    })

    // Click to open if it's closed
    if (accordionHeader.getAttribute('aria-expanded') === 'false') {
      await accordionHeader.click()
    }

    // Wait for accordion to open and verify reference paths are displayed
    await waitFor(async () => {
      const referencePaths = canvas.getAllByTestId('reference-path')
      expect(referencePaths).toHaveLength(2)
      expect(referencePaths[0]).toHaveTextContent(
        'src/web/components/organisms/ReferenceList/index.tsx'
      )
      expect(referencePaths[1]).toHaveTextContent(
        'src/web/components/organisms/ReferenceList/style.css.ts'
      )
    })
  }
}

/**
 * Empty state with no references.
 */
export const Empty: Story = {
  args: {
    sessionDetail: {
      sessionId: 'session-456',
      references: []
    } as unknown as SessionDetail
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify summary text for 0 references
    await expect(canvas.getByText(/0 references/i)).toBeInTheDocument()

    // Find the accordion header and open it if closed
    const accordionHeader = canvas.getByRole('button', {
      name: /advanced settings/i
    })

    // Click to open if it's closed
    if (accordionHeader.getAttribute('aria-expanded') === 'false') {
      await accordionHeader.click()
    }

    // Wait for accordion to open and verify the empty message is displayed
    await waitFor(async () => {
      expect(canvas.getByText('No references added yet.')).toBeInTheDocument()
    })
  }
}

/**
 * Demonstrates error display (line 80 coverage).
 */
export const WithError: Story = {
  args: {
    sessionDetail: {
      sessionId: 'session-789',
      references: []
    } as unknown as SessionDetail
  },
  render: (arguments_): JSX.Element => {
    const FormWithError = (): JSX.Element => {
      const methods = useFormContext()

      const handleSubmit = async (): Promise<void> => {
        await methods.trigger('references')
      }

      return (
        <>
          <ReferenceList {...arguments_} />
          <Button type="button" onClick={handleSubmit}>
            Trigger Validation
          </Button>
        </>
      )
    }

    const schema = z.object({
      references: z.array(z.any()).min(1, 'At least one reference is required')
    })

    return (
      <Form schema={schema} defaultValues={{ references: [] }}>
        <FormWithError />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Trigger validation
    const button = canvas.getByRole('button', { name: /trigger validation/i })
    await userEvent.click(button)

    // Find the accordion header and open it if closed
    const accordionHeader = canvas.getByRole('button', {
      name: /advanced settings/i
    })

    // Click to open if it's closed
    if (accordionHeader.getAttribute('aria-expanded') === 'false') {
      await accordionHeader.click()
    }

    // Wait for error message to appear
    await waitFor(async () => {
      const errorMessage = canvas.getByText(/at least one reference is required/i)
      expect(errorMessage).toBeInTheDocument()
    })
  }
}
