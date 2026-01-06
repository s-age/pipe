import type { JSX } from 'react'

import { IconBulkDelete } from '@/components/atoms/IconBulkDelete'
import { Flex } from '@/components/molecules/Flex'
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
    closeModal,
    handleOverlayPointerDown,
    handleResultKeyDown,
    handleResultPointerDown,
    handleSubmit,
    open,
    query,
    results,
    setQuery
  } = useSearchSessionsHandlers()

  return (
    <Flex as="header" align="center" className={headerContainer}>
      <Flex align="center" gap="s" className={brand}>
        <img src={logoSource} alt="pipe logo" className={brandLogo} />
      </Flex>
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
                results.map((r: { sessionId: string; title: string }) => (
                  <div
                    key={r.sessionId}
                    className={searchResultItem}
                    role="button"
                    tabIndex={0}
                    data-session-id={r.sessionId}
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
    </Flex>
  )
}
