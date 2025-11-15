import React, { useCallback } from 'react'

import { Fieldset } from '@/components/molecules/Fieldset'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { metaItem, metaItemLabel } from './style.css'

type ArtifactsSelectorProperties = {
  legend?: string
}

export const ArtifactsSelector = ({
  legend = 'Artifacts:'
}: ArtifactsSelectorProperties): React.JSX.Element => {
  const formContext = useOptionalFormContext()
  const setValue = formContext?.setValue
  const currentValue = formContext?.watch?.('artifacts') || []

  const handleArtifactsChange = useCallback(
    (values: string[]) => {
      if (setValue) {
        setValue('artifacts', values)
      }
    },
    [setValue]
  )

  return (
    <Fieldset
      legend={<span className={metaItemLabel}>{legend}</span>}
      className={metaItem}
    >
      <FileSearchExplorer existsValue={currentValue} onChange={handleArtifactsChange} />
    </Fieldset>
  )
}
