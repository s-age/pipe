import type { JSX } from 'react'

import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import TextArea from '@/components/atoms/TextArea'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { metaItem, metaItemLabel, inputFullWidth, textareaFullWidth } from './style.css'
import { useSessionBasicMeta } from './useSessionBasicMeta'

type SessionBasicMetaFormProperties = {
  sessionDetail: SessionDetail | null
}

export const SessionBasicMetaForm = ({
  sessionDetail,
}: SessionBasicMetaFormProperties): JSX.Element => {
  const {
    purpose,
    setPurpose,
    handlePurposeBlur,
    background,
    setBackground,
    handleBackgroundBlur,
    roles,
    setRoles,
    handleRolesBlur,
    procedure,
    setProcedure,
    handleProcedureBlur,
    artifacts,
    setArtifacts,
    handleArtifactsBlur,
  } = useSessionBasicMeta({ sessionDetail })

  return (
    <>
      <div className={metaItem}>
        <Label htmlFor="purpose" className={metaItemLabel}>
          Purpose:
        </Label>
        <InputText
          id="purpose"
          value={purpose}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
            setPurpose(event.target.value)
          }
          onBlur={handlePurposeBlur}
          className={inputFullWidth}
        />
      </div>
      <div className={metaItem}>
        <Label htmlFor="background" className={metaItemLabel}>
          Background:
        </Label>
        <TextArea
          id="background"
          value={background}
          onChange={(event: React.ChangeEvent<HTMLTextAreaElement>) =>
            setBackground(event.target.value)
          }
          onBlur={handleBackgroundBlur}
          className={textareaFullWidth}
        />
      </div>
      <div className={metaItem}>
        <Label htmlFor="roles" className={metaItemLabel}>
          Roles:
        </Label>
        <InputText
          id="roles"
          value={roles}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
            setRoles(event.target.value)
          }
          onBlur={handleRolesBlur}
          className={inputFullWidth}
        />
      </div>
      <div className={metaItem}>
        <Label htmlFor="procedure" className={metaItemLabel}>
          Procedure:
        </Label>
        <InputText
          id="procedure"
          value={procedure}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
            setProcedure(event.target.value)
          }
          onBlur={handleProcedureBlur}
          className={inputFullWidth}
        />
      </div>
      <div className={metaItem}>
        <Label htmlFor="artifacts" className={metaItemLabel}>
          Artifacts:
        </Label>
        <InputText
          id="artifacts"
          value={artifacts}
          onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
            setArtifacts(event.target.value)
          }
          onBlur={handleArtifactsBlur}
          className={inputFullWidth}
        />
      </div>
    </>
  )
}
