import React from 'react'

import { Fieldset } from '@/components/molecules/Fieldset'
import { MetaItem, MetaLabel } from '@/components/molecules/MetaItem'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'

import { useArtifactsSelectorHandlers } from './hooks/useArtifactsSelectorHandlers'

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
    <MetaItem>
      <Fieldset legend={<MetaLabel>{legend}</MetaLabel>}>
        <FileSearchExplorer
          existsValue={currentValue}
          onChange={handleArtifactsChange}
        />
      </Fieldset>
    </MetaItem>
  )
}
