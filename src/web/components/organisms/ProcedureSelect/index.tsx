import { useCallback, useEffect, useState } from 'react'
import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { ProcedureOption } from '@/lib/api/procedures/getProcedures'

import { useProceduresActions } from './hooks/useProceduresActions'
import { container } from './style.css'

type ProcedureSelectProperties = {
  placeholder?: string
}

export const ProcedureSelect = (properties: ProcedureSelectProperties): JSX.Element => {
  const { placeholder = 'Select procedure' } = properties

  const formContext = useOptionalFormContext()
  const setValue = formContext?.setValue
  const currentValue = formContext?.watch?.('procedure') || ''
  const error = formContext?.formState?.errors?.procedure

  const [procedureOptions, setProcedureOptions] = useState<ProcedureOption[]>([])
  const { fetchProcedures } = useProceduresActions()

  useEffect(() => {
    const loadProcedures = async (): Promise<void> => {
      try {
        const procedures = await fetchProcedures()
        setProcedureOptions(procedures)
      } catch (error) {
        console.error('Failed to fetch procedures:', error)
      }
    }
    void loadProcedures()
  }, [fetchProcedures])

  const handleProcedureChange = useCallback(
    (values: string[]): void => {
      if (setValue) {
        setValue('procedure', values[0] || '')
      }
    },
    [setValue]
  )

  const list = procedureOptions.map((proc) => ({
    label: proc.label,
    value: proc.value
  }))

  const existsValue = currentValue ? [currentValue] : []

  return (
    <div className={container}>
      <FileSearchExplorer
        existsValue={existsValue}
        list={list}
        isMultiple={false}
        placeholder={placeholder}
        onChange={handleProcedureChange}
      />
      {error && <ErrorMessage error={error as never} />}
    </div>
  )
}
