import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse, delay } from 'msw'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { Therapist } from '../index'
import type { Diagnosis } from '../types'

const mockSessionDetail: Partial<SessionDetail> = {
  sessionId: 'session-1234567890',
  turns: [
    {
      type: 'user_task',
      instruction: 'Turn 1 content',
      timestamp: new Date().toISOString()
    },
    {
      type: 'model_response',
      content: 'Turn 2 content',
      timestamp: new Date().toISOString()
    },
    {
      type: 'user_task',
      instruction: 'Turn 3 content',
      timestamp: new Date().toISOString()
    }
  ]
}

const mockDiagnosis: Diagnosis = {
  summary:
    'The session contains some redundant turns and could be improved by editing turn 2.',
  deletions: [1],
  edits: [{ turn: 2, newContent: 'Improved content for turn 2' }],
  compressions: [{ start: 1, end: 2, reason: 'Redundant interaction' }],
  rawDiagnosis: 'Raw diagnosis data for debugging'
}

const Meta = {
  title: 'Organisms/Therapist',
  component: Therapist,
  tags: ['autodocs'],
  args: {
    sessionDetail: mockSessionDetail as SessionDetail,
    onRefresh: fn(async () => {
      console.log('onRefresh called')
    })
  }
} satisfies StoryMeta<typeof Therapist>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Initial state of the Therapist component before diagnosis.
 */
export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail as SessionDetail
  }
}

/**
 * State of the Therapist component showing diagnosis results.
 * This uses MSW to mock the diagnosis response.
 */
export const WithDiagnosis: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post(`${API_BASE_URL}/therapist`, () =>
          HttpResponse.json({
            diagnosis: mockDiagnosis,
            sessionId: mockSessionDetail.sessionId
          })
        )
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const diagnoseButton = canvas.getByRole('button', { name: /start diagnosis/i })

    await userEvent.click(diagnoseButton)

    // Wait for diagnosis results to appear
    await waitFor(() => expect(canvas.getByText(/summary:/i)).toBeInTheDocument(), {
      timeout: 2000
    })
    await expect(canvas.getByText(mockDiagnosis.summary)).toBeInTheDocument()
  }
}

/**
 * Demonstrates the full flow: Diagnosis -> Selection -> Application.
 */
export const FullFlow: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post(`${API_BASE_URL}/therapist`, async () => {
          await delay(500)

          return HttpResponse.json({
            diagnosis: mockDiagnosis,
            sessionId: mockSessionDetail.sessionId
          })
        }),
        http.post(`${API_BASE_URL}/doctor`, async () => {
          await delay(500)

          return HttpResponse.json({
            result: { status: 'Succeeded' },
            sessionId: mockSessionDetail.sessionId
          })
        })
      ]
    }
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // 1. Start Diagnosis
    const diagnoseButton = canvas.getByRole('button', { name: /start diagnosis/i })
    await userEvent.click(diagnoseButton)

    // 2. Wait for results
    const summaryHeading = await canvas.findByText(/summary:/i, {}, { timeout: 3000 })
    await expect(summaryHeading).toBeInTheDocument()

    // 3. Select a modification (Deletion)
    const deletionCheckbox = canvas.getByLabelText(/turn 1: suggested removal/i)
    await userEvent.click(deletionCheckbox)

    // 4. Apply modifications
    const applyButton = canvas.getByRole('button', {
      name: /apply selected modifications/i
    })
    await expect(applyButton).toBeEnabled()
    await userEvent.click(applyButton)

    // 5. Verify onRefresh was called
    await waitFor(() => expect(args.onRefresh).toHaveBeenCalled(), {
      timeout: 3000
    })

    // 6. Verify it returned to the initial state (form)
    await waitFor(() =>
      expect(
        canvas.getByRole('button', { name: /start diagnosis/i })
      ).toBeInTheDocument()
    )
  }
}

/**
 * Demonstrates null sessionDetail to cover index.tsx:25-26
 */
export const NullSessionDetail: Story = {
  args: {
    sessionDetail: null
  }
}

/**
 * Demonstrates empty diagnosis results (no deletions, edits, compressions)
 * to cover TherapistResult.tsx:60-88 branch coverage
 */
export const EmptyDiagnosisResults: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post(`${API_BASE_URL}/therapist`, () =>
          HttpResponse.json({
            diagnosis: {
              summary: 'No issues found in the session.',
              deletions: null,
              edits: null,
              compressions: null,
              rawDiagnosis: 'No modifications needed'
            },
            sessionId: mockSessionDetail.sessionId
          })
        )
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const diagnoseButton = canvas.getByRole('button', { name: /start diagnosis/i })

    await userEvent.click(diagnoseButton)

    // Wait for diagnosis results with "None" items
    await waitFor(() => expect(canvas.getByText(/summary:/i)).toBeInTheDocument(), {
      timeout: 2000
    })

    // Verify "None" is displayed for each category
    const noneItems = canvas.getAllByText(/none/i)
    expect(noneItems.length).toBeGreaterThanOrEqual(3) // Deletions, Edits, Compressions
  }
}
