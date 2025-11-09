import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { z } from 'zod'

import { Button } from '@/components/atoms/Button'
import { InputCheckbox } from '@/components/atoms/InputCheckbox'
import { InputRadio } from '@/components/atoms/InputRadio'
import { InputText } from '@/components/atoms/InputText'
import { TextArea } from '@/components/atoms/TextArea'
import { Fieldset } from '@/components/molecules/Fieldset'
import { Slider } from '@/components/molecules/Slider'
import { Form, useFormContext } from '@/components/organisms/Form'

const Meta = {
  title: 'Organisms/Form — Manual',
  // We use a loose Meta type to avoid forcing `args` for Form's required props
  tags: ['autodocs'],
} satisfies StoryMeta<unknown>

export default Meta
type Story = StoryObj<typeof Meta>

// This story is intended as an annotated manual for LLMs and humans alike.
// It demonstrates how to compose the project's form primitives both with
// react-hook-form (via the `Form` provider) and in a plain HTML <form>.

export const Manual: Story = {
  render: (): JSX.Element => {
    const WithRHFExample = (): JSX.Element => {
      const InnerForm = (): JSX.Element => {
        const methods = useFormContext()

        return (
          <div style={{ display: 'grid', gap: 8 }}>
            <Fieldset legend="Name">
              {() => (
                <InputText
                  name="firstName"
                  placeholder="First name"
                  register={methods.register}
                />
              )}
            </Fieldset>

            <Fieldset legend="Choose one" hint="Pick a single option">
              {(ids) => (
                <div style={{ display: 'grid', gap: 6 }}>
                  <InputRadio
                    name="choice"
                    value="a"
                    register={methods.register}
                    aria-describedby={[ids.hintId, ids.errorId]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    Option A
                  </InputRadio>
                  <InputRadio
                    name="choice"
                    value="b"
                    register={methods.register}
                    aria-describedby={[ids.hintId, ids.errorId]
                      .filter(Boolean)
                      .join(' ')}
                  >
                    Option B
                  </InputRadio>
                </div>
              )}
            </Fieldset>

            <Fieldset legend="Agreement">
              {(ids) => (
                <InputCheckbox
                  name="agree"
                  register={methods.register}
                  aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
                >
                  Agree to terms
                </InputCheckbox>
              )}
            </Fieldset>

            <Fieldset legend="Notes">
              {(ids) => (
                <TextArea
                  name="notes"
                  rows={4}
                  placeholder="Notes"
                  register={methods.register}
                  aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
                />
              )}
            </Fieldset>

            <Fieldset legend="Rating" hint="0 = low, 100 = high">
              {(ids) => (
                <Slider
                  name="rating"
                  min={0}
                  max={100}
                  register={methods.register}
                  aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
                />
              )}
            </Fieldset>

            <div style={{ display: 'flex', gap: 8 }}>
              <Button type="submit">Submit</Button>
              <Button type="button" kind="ghost">
                Cancel
              </Button>
            </div>
          </div>
        )
      }

      const schema = z.object({
        firstName: z.string().min(1, 'First name is required'),
        choice: z.string(),
        agree: z.boolean().optional(),
        notes: z.string().optional(),
        rating: z.number().min(0).max(100).optional(),
      })

      const defaultValues = {
        // provide a valid example so initial submit succeeds in the story
        firstName: 'Alice',
        choice: 'a',
        agree: false,
        notes: '',
        // keep rating centered as an example; change to 0 if you want left-aligned
        rating: 50,
      }

      const handleSubmit = (data: unknown): void => {
        console.log('RHF submit (via Form)', data)
      }

      return (
        <div style={{ padding: 12, border: '1px solid #eee', borderRadius: 6 }}>
          <h3>With react-hook-form (Form + useFormContext)</h3>
          <p style={{ marginTop: 0 }}>
            Use <code>Form</code> to create RHF methods and provide them in context;
            nested controls call <code>useFormContext()</code> to access `register` and
            other APIs.
          </p>

          <Form onSubmit={handleSubmit} schema={schema} defaultValues={defaultValues}>
            <InnerForm />
          </Form>
        </div>
      )
    }

    return (
      <div style={{ display: 'grid', gap: 16 }}>
        <p>
          This manual demonstrates the canonical patterns for wiring form controls in
          this codebase. Use the RHF example for complex forms that need validation and
          programmatic control. Use the plain form example when you prefer minimal
          dependencies or server-side form handling.
        </p>

        <WithRHFExample />
      </div>
    )
  },
}
