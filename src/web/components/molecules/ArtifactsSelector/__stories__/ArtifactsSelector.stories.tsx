import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { z } from 'zod'

import { Form, useFormContext } from '@/components/organisms/Form'

import { ArtifactsSelector } from '../index'

const Meta = {
  title: 'Molecules/ArtifactsSelector',
  component: ArtifactsSelector,
  tags: ['autodocs']
} satisfies StoryMeta<typeof ArtifactsSelector>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    legend: 'Artifacts:'
  }
}

export const CustomLegend: Story = {
  args: {
    legend: 'Select Files:'
  }
}

const ArtifactsWatcher = (): JSX.Element => {
  const { watch } = useFormContext()
  const artifacts = watch('artifacts') || []

  return (
    <div style={{ marginTop: '1rem', padding: '0.5rem', background: '#f5f5f5' }}>
      <strong>Current Form State (artifacts):</strong>
      <pre>{JSON.stringify(artifacts, null, 2)}</pre>
    </div>
  )
}

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const schema = z.object({
      artifacts: z.array(z.string()).min(1, 'At least one artifact is required')
    })

    const FormExample = (): JSX.Element => (
      <Form schema={schema} defaultValues={{ artifacts: ['src/index.ts'] }}>
        <ArtifactsSelector legend="Form Integrated Selector" />
        <ArtifactsWatcher />
        <div style={{ marginTop: '1rem' }}>
          <p>Try adding or removing artifacts to see form state changes.</p>
        </div>
      </Form>
    )

    return <FormExample />
  }
}
