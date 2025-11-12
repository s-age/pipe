import React, { useCallback, useMemo } from 'react'
import { useWatch } from 'react-hook-form'

import { Button } from '@/components/atoms/Button'
import { Fieldset } from '@/components/molecules/Fieldset'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'

import {
  metaItem,
  metaItemLabel,
  artifactsList,
  artifactItem,
  artifactPath,
  removeArtifactButton,
  debugInfo
} from './style.css'

type ArtifactsSelectorProperties = {
  legend?: string
}

export const ArtifactsSelector = ({
  legend = 'Artifacts:'
}: ArtifactsSelectorProperties): React.JSX.Element => {
  const formContext = useOptionalFormContext()
  const setValue = formContext?.setValue
  const getValues = formContext?.getValues
  const watchedArtifacts = useWatch({
    control: formContext?.control,
    name: 'artifacts'
    // defaultValue: []
  })

  // Try to get the current value directly from form
  const currentArtifacts = getValues ? getValues('artifacts') : undefined

  console.log('ArtifactsSelector - watchedArtifacts:', watchedArtifacts)
  console.log('ArtifactsSelector - currentArtifacts (getValues):', currentArtifacts)
  console.log('ArtifactsSelector - formContext:', formContext)

  const selectedArtifacts: string[] = useMemo(() => {
    if (Array.isArray(watchedArtifacts)) {
      return watchedArtifacts
    }
    if (typeof watchedArtifacts === 'string') {
      return watchedArtifacts.split(', ').filter(Boolean)
    }

    return []
  }, [watchedArtifacts])

  const handleArtifactsPathChange = useCallback(
    (paths: string[]) => {
      console.log('handleArtifactsPathChange called with:', paths)
      if (setValue) {
        setValue('artifacts', paths.join(', '))
        console.log('setValue called with:', paths.join(', '))
      }
    },
    [setValue]
  )

  const handleRemoveArtifact = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      const index = parseInt(event.currentTarget.getAttribute('data-index') || '0', 10)
      const newArtifacts = selectedArtifacts.filter(
        (_: string, i: number) => i !== index
      )

      if (setValue) {
        setValue('artifacts', newArtifacts.join(', '))
      }
    },
    [selectedArtifacts, setValue]
  )

  return (
    <Fieldset
      legend={<span className={metaItemLabel}>{legend}</span>}
      className={metaItem}
    >
      <div className={debugInfo}>
        Debug: watchedArtifacts = {JSON.stringify(watchedArtifacts)} (type:{' '}
        {typeof watchedArtifacts})
      </div>
      <div className={debugInfo}>
        Debug: currentArtifacts = {JSON.stringify(currentArtifacts)} (type:{' '}
        {typeof currentArtifacts})
      </div>
      <FileSearchExplorer onPathChange={handleArtifactsPathChange} />
      {selectedArtifacts.length > 0 && (
        <div className={artifactsList}>
          {selectedArtifacts.map((artifact: string, index: number) => (
            <div key={index} className={artifactItem}>
              <span className={artifactPath}>{artifact}</span>
              <Button
                kind="ghost"
                size="xsmall"
                onClick={handleRemoveArtifact}
                data-index={index}
                className={removeArtifactButton}
              >
                ×
              </Button>
            </div>
          ))}
        </div>
      )}
    </Fieldset>
  )
}
