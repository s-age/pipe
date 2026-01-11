import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, within } from 'storybook/test'

import {
  renderTurnOptions,
  getTurnOptions,
  getTurnOptionsDisableBelow
} from '../TurnOptions'

const Meta = {
  title: 'Organisms/Compressor/TurnOptions',
  tags: ['autodocs']
} satisfies StoryMeta

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Tests renderTurnOptions with limit <= 0 (line 9 coverage).
 */
export const RenderWithZeroLimit: Story = {
  render: (): JSX.Element => {
    const options = renderTurnOptions(0, undefined)

    return <div data-testid="options">{options}</div>
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const container = canvas.getByTestId('options')
    await expect(container).toBeEmptyDOMElement()
  }
}

/**
 * Tests renderTurnOptions with disableAbove specified (lines 15-17 coverage).
 */
export const RenderWithDisableAbove: Story = {
  render: (): JSX.Element => {
    const options = renderTurnOptions(5, 3)

    return <select data-testid="select">{options}</select>
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const select = canvas.getByTestId('select')
    const allOptions = within(select).getAllByRole('option')
    await expect(allOptions).toHaveLength(5)

    // Options 4 and 5 should be disabled (turn > 3)
    await expect(allOptions[3]).toBeDisabled()
    await expect(allOptions[4]).toBeDisabled()
  }
}

/**
 * Tests getTurnOptions with limit <= 0 (line 28 coverage).
 */
export const GetOptionsWithZeroLimit: Story = {
  render: (): JSX.Element => {
    const options = getTurnOptions(0, undefined)

    return <div data-testid="result">{JSON.stringify(options)}</div>
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const result = canvas.getByTestId('result')
    await expect(result).toHaveTextContent('[]')
  }
}

/**
 * Tests getTurnOptions with disableFrom specified (lines 33-34 coverage).
 */
export const GetOptionsWithDisableFrom: Story = {
  render: (): JSX.Element => {
    const options = getTurnOptions(5, 3)

    return (
      <div data-testid="result">
        {options.map((opt, i) => (
          <div key={i} data-disabled={opt.disabled}>
            {opt.label}
          </div>
        ))}
      </div>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const items = canvas.getAllByText(/\d/)
    await expect(items).toHaveLength(5)

    // Options with turn >= 3 should be disabled (3, 4, 5)
    await expect(items[2]).toHaveAttribute('data-disabled', 'true')
    await expect(items[3]).toHaveAttribute('data-disabled', 'true')
    await expect(items[4]).toHaveAttribute('data-disabled', 'true')
  }
}

/**
 * Tests getTurnOptionsDisableBelow with limit <= 0 (line 42 coverage).
 */
export const GetOptionsDisableBelowWithZeroLimit: Story = {
  render: (): JSX.Element => {
    const options = getTurnOptionsDisableBelow(0, undefined)

    return <div data-testid="result">{JSON.stringify(options)}</div>
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const result = canvas.getByTestId('result')
    await expect(result).toHaveTextContent('[]')
  }
}

/**
 * Tests getTurnOptionsDisableBelow with disableBelow specified (lines 47-48 coverage).
 */
export const GetOptionsDisableBelowWithThreshold: Story = {
  render: (): JSX.Element => {
    const options = getTurnOptionsDisableBelow(5, 3)

    return (
      <div data-testid="result">
        {options.map((opt, i) => (
          <div key={i} data-disabled={opt.disabled}>
            {opt.label}
          </div>
        ))}
      </div>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const items = canvas.getAllByText(/\d/)
    await expect(items).toHaveLength(5)

    // Options with turn <= 3 should be disabled (1, 2, 3)
    await expect(items[0]).toHaveAttribute('data-disabled', 'true')
    await expect(items[1]).toHaveAttribute('data-disabled', 'true')
    await expect(items[2]).toHaveAttribute('data-disabled', 'true')
  }
}

/**
 * Tests renderTurnOptions with empty string for disableAbove (line 16 coverage).
 */
export const RenderWithEmptyStringDisable: Story = {
  render: (): JSX.Element => {
    const options = renderTurnOptions(3, '')

    return <select data-testid="select">{options}</select>
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const select = canvas.getByTestId('select')
    const allOptions = within(select).getAllByRole('option')
    await expect(allOptions).toHaveLength(3)

    // All options should be enabled when disableAbove is ''
    allOptions.forEach(async (option) => {
      await expect(option).not.toBeDisabled()
    })
  }
}
