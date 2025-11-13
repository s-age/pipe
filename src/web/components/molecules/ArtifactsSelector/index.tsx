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

  const handleArtifactsPathChange = useCallback(
    (paths: string[]) => {
      if (setValue) {
        setValue('artifacts', paths)
      }
    },
    [setValue]
  )

  return (
    <Fieldset
      legend={<span className={metaItemLabel}>{legend}</span>}
      className={metaItem}
    >
      <FileSearchExplorer onPathChange={handleArtifactsPathChange} />
    </Fieldset>
  )
}
