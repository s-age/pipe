import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { useProceduresActions } from './hooks/useProceduresActions'
import { useProceduresHandlers } from './hooks/useProceduresHandlers'
import { container } from './style.css'

type ProcedureSelectProperties = {
  placeholder?: string
}

export const ProcedureSelect = (properties: ProcedureSelectProperties): JSX.Element => {
  const { placeholder = 'Select procedure' } = properties

  const formContext = useOptionalFormContext()
  const currentValue = formContext?.watch?.('procedure') || ''
  const error = formContext?.formState?.errors?.procedure

  const actions = useProceduresActions()
  const { procedureOptions, handleFocus, handleProcedureChange } =
    useProceduresHandlers(actions, formContext)

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
        onFocus={handleFocus}
      />
      {error && <ErrorMessage error={error as never} />}
    </div>
  )
}
