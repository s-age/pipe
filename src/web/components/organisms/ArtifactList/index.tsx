import type { JSX } from 'react'

import { Label } from '@/components/atoms/Label'
import { MetaLabel, MetaItem } from '@/components/molecules/MetaItem'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useArtifactListHandlers } from './hooks/useArtifactListHandlers'
import { useArtifactListLifecycle } from './hooks/useArtifactListLifecycle'

type ArtifactListProperties = {
  sessionDetail: SessionDetail
  refreshSessions: () => Promise<void>
}

export const ArtifactList = ({
  sessionDetail,
  refreshSessions
}: ArtifactListProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const artifacts = formContext?.watch('artifacts') || []

  const { handleArtifactsChange } = useArtifactListHandlers({
    sessionDetail,
    formContext,
    refreshSessions
  })

  useArtifactListLifecycle({
    sessionDetail,
    formContext,
    currentArtifacts: artifacts
  })

  return (
    <MetaItem>
      <Label>
        <MetaLabel>Artifacts:</MetaLabel>
      </Label>

      <FileSearchExplorer
        existsValue={artifacts}
        placeholder="Type to search files... (select from suggestions)"
        onChange={handleArtifactsChange}
      />
    </MetaItem>
  )
}
