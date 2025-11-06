import { JSX } from 'react'

import InputText from '@/components/atoms/InputText'
import Label from '@/components/atoms/Label'
import TextArea from '@/components/atoms/TextArea'
import { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { SessionDetail } from '@/lib/api/session/getSession'

import { metaItem, metaItemLabel, inputFullWidth, textareaFullWidth } from './style.css'
import { useSessionBasicMeta } from './useSessionBasicMeta'

type SessionBasicMetaFormProps = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  onMetaSave: (sessionId: string, meta: EditSessionMetaRequest) => void
}

export const SessionBasicMetaForm = ({
  sessionDetail,
  currentSessionId,
  onMetaSave,
}: SessionBasicMetaFormProps): JSX.Element => {
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
  } = useSessionBasicMeta({ sessionDetail, currentSessionId, onMetaSave })

  return (
    <>
      <div className={metaItem}>
        <Label htmlFor="purpose" className={metaItemLabel}>
          Purpose:
        </Label>
        <InputText
          id="purpose"
          value={purpose}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setPurpose(e.target.value)
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
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
            setBackground(e.target.value)
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setRoles(e.target.value)
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setProcedure(e.target.value)
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setArtifacts(e.target.value)
          }
          onBlur={handleArtifactsBlur}
          className={inputFullWidth}
        />
      </div>
    </>
  )
}
