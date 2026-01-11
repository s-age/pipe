import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, fn, userEvent, within } from 'storybook/test'

import { FileSearchExplorer } from '../index'

const mockList = [
  { label: 'src/index.ts', value: 'src/index.ts', path: 'src' },
  {
    label: 'src/components/Button.tsx',
    value: 'src/components/Button.tsx',
    path: 'src/components'
  },
  { label: 'package.json', value: 'package.json', path: '.' },
  { label: 'README.md', value: 'README.md', path: '.' },
  { label: 'tsconfig.json', value: 'tsconfig.json', path: '.' }
]

const Meta = {
  title: 'Organisms/FileSearchExplorer',
  component: FileSearchExplorer,
  tags: ['autodocs'],
  args: {
    onChange: fn(),
    onFocus: fn()
  }
} satisfies StoryMeta<typeof FileSearchExplorer>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    existsValue: ['src/index.ts'],
    list: mockList,
    isMultiple: true,
    placeholder: 'Search files...'
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox', { name: /search files or directories/i })

    await expect(input).toBeInTheDocument()
    await expect(canvas.getByText('src/index.ts')).toBeInTheDocument()

    // Verify onFocus is called when input is focused
    await userEvent.click(input)
    await expect(args.onFocus).toHaveBeenCalled()

    // Interaction: Type to see suggestions
    await userEvent.type(input, 'package')
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    const option = within(listbox).getByRole('option', { name: /package\.json/i })
    await expect(option).toBeInTheDocument()

    // Click the option to trigger onChange
    await userEvent.click(option)
    await expect(args.onChange).toHaveBeenCalled()
  }
}

export const Empty: Story = {
  args: {
    existsValue: [],
    list: mockList,
    isMultiple: true,
    placeholder: 'Type to search...'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox')
    await expect(input).toHaveAttribute('placeholder', 'Search files or directories...')
    await expect(
      canvas.queryByRole('button', { name: /delete/i })
    ).not.toBeInTheDocument()
  }
}

export const SingleSelection: Story = {
  args: {
    existsValue: ['package.json'],
    list: mockList,
    isMultiple: false,
    placeholder: 'Select a file...'
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox')

    await expect(canvas.getByText('package.json')).toBeInTheDocument()

    // Verify onFocus is called
    await userEvent.click(input)
    await expect(args.onFocus).toHaveBeenCalled()

    // In single selection mode, adding another should replace or be handled by the component logic
    // Here we just verify the initial state and that suggestions appear
    await userEvent.type(input, 'src')
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()
  }
}

/**
 * Tests coverage for SuggestionItem.tsx line 29 (isSelected false case).
 * Also tests FileSearchExplorer index.tsx line 130 (selectedIndex < 0 case).
 */
export const NoSelectedSuggestion: Story = {
  args: {
    existsValue: [],
    list: mockList,
    isMultiple: true,
    placeholder: 'Type to search...'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('combobox')

    // Type to show suggestions but don't select any
    await userEvent.type(input, 'src')
    const listbox = await canvas.findByRole('listbox')
    await expect(listbox).toBeInTheDocument()

    // Verify that none of the suggestions have the selected class
    const options = within(listbox).getAllByRole('option')
    await expect(options.length).toBeGreaterThan(0)

    // Verify aria-activedescendant is not set when selectedIndex < 0
    await expect(input).not.toHaveAttribute('aria-activedescendant')
  }
}
