import type { JSX } from 'react'

import { IconBulkDelete } from '@/components/atoms/IconBulkDelete'
import { InputSearch } from '@/components/molecules/InputSearch'
import { Tooltip } from '@/components/organisms/Tooltip'
import logoSource from '@/static/images/logo.png'

import { useSearchSessionsHandlers } from './hooks/useSearchSessionsHandlers'
import {
  headerContainer,
  brand,
  brandLogo,
  searchWrapper,
  sessionManagementLink,
  searchModalOverlay,
  searchModalContent,
  searchModalHeader,
  searchModalClose,
  searchResultItem,
  searchNoResults,
  searchModalHeaderText
} from './style.css'

export const Header = (): JSX.Element => {
  const {
    query,
    setQuery,
    results,
    open,
    handleSubmit,
    closeModal,
    handleOverlayPointerDown,
    handleResultPointerDown,
    handleResultKeyDown
  } = useSearchSessionsHandlers()

  return (
    <header className={headerContainer}>
      <div className={brand}>
        <img src={logoSource} alt="pipe logo" className={brandLogo} />
      </div>
      <div className={searchWrapper}>
        <InputSearch
          placeholder="Search sessions..."
          value={query}
          onChange={setQuery}
          onSubmit={handleSubmit}
          name="site_search"
        />
        <Tooltip content="Session Management" placement="bottom">
          <a
            href="/session_management"
            className={sessionManagementLink}
            aria-label="Session Management"
          >
            <IconBulkDelete size={18} />
          </a>
        </Tooltip>

        {open && (
          <div
            className={searchModalOverlay}
            role="dialog"
            aria-modal="true"
            onMouseDown={handleOverlayPointerDown}
          >
            <div className={searchModalContent}>
              <div className={searchModalHeader}>
                <div className={searchModalHeaderText}>Search results</div>
                <button
                  className={searchModalClose}
                  onClick={closeModal}
                  aria-label="Close search"
                >
                  ✕
                </button>
              </div>

              {results.length === 0 ? (
                <div className={searchNoResults}>No results</div>
              ) : (
                results.map((r: { session_id: string; title: string }) => (
                  <div
                    key={r.session_id}
                    className={searchResultItem}
                    role="button"
                    tabIndex={0}
                    data-session-id={r.session_id}
                    onMouseDown={handleResultPointerDown}
                    onKeyDown={handleResultKeyDown}
                  >
                    {r.title}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
