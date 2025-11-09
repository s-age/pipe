import type { JSX } from 'react'

import { InputText } from '@/components/atoms/InputText'
import { TextArea } from '@/components/atoms/TextArea'
import { Fieldset } from '@/components/molecules/Fieldset'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { metaItem, metaItemLabel, inputFullWidth, textareaFullWidth } from './style.css'

type SessionBasicMetaFormProperties = {
  sessionDetail: SessionDetail | null
}

export const SessionBasicMetaForm = ({
  sessionDetail: _sessionDetail,
}: SessionBasicMetaFormProperties): JSX.Element => {
  const register = useOptionalFormContext()?.register

  return (
    <>
      <Fieldset
        legend={<span className={metaItemLabel}>Purpose:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="purpose"
            register={register}
            name="purpose"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Background:</span>}
        className={metaItem}
      >
        {(ids) => (
          <TextArea
            id="background"
            register={register}
            name="background"
            className={textareaFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Roles:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="roles"
            register={register}
            name="roles"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Procedure:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="procedure"
            register={register}
            name="procedure"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>

      <Fieldset
        legend={<span className={metaItemLabel}>Artifacts:</span>}
        className={metaItem}
      >
        {(ids) => (
          <InputText
            id="artifacts"
            register={register}
            name="artifacts"
            className={inputFullWidth}
            aria-describedby={[ids.hintId, ids.errorId].filter(Boolean).join(' ')}
          />
        )}
      </Fieldset>
    </>
  )
}
