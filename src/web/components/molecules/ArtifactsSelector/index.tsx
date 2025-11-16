import React from 'react'

import { Fieldset } from '@/components/molecules/Fieldset'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { useArtifactsSelectorHandlers } from './hooks/useArtifactsSelectorHandlers'
import { metaItem, metaItemLabel } from './style.css'

type ArtifactsSelectorProperties = {
  legend?: string
}

export const ArtifactsSelector = ({
  legend = 'Artifacts:'
}: ArtifactsSelectorProperties): React.JSX.Element => {
  const formContext = useOptionalFormContext()
  const watch = formContext?.watch
  const currentValue = watch ? watch('artifacts') || [] : []

  const { handleArtifactsChange } = useArtifactsSelectorHandlers(formContext)

  return (
    <Fieldset
      legend={<span className={metaItemLabel}>{legend}</span>}
      className={metaItem}
    >
      <FileSearchExplorer existsValue={currentValue} onChange={handleArtifactsChange} />
    </Fieldset>
  )
}
