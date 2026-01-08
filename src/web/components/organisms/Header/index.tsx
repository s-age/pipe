import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { IconBulkDelete } from '@/components/atoms/IconBulkDelete'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { InputSearch } from '@/components/molecules/InputSearch'
import { Link } from '@/components/molecules/Link'
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
      <Flex className={searchWrapper} align="center" justify="center">
        <InputSearch
          placeholder="Search sessions..."
          value={query}
          onChange={setQuery}
          onSubmit={handleSubmit}
          name="site_search"
        />
        <Tooltip content="Session Management" placement="bottom">
          <Link
            href="/session_management"
            className={sessionManagementLink}
            aria-label="Session Management"
          >
            <IconBulkDelete size={18} />
          </Link>
        </Tooltip>

        {open && (
          <Flex
            className={searchModalOverlay}
            role="dialog"
            aria-modal="true"
            aria-labelledby="search-modal-title"
            aria-describedby="search-modal-description"
            onMouseDown={handleOverlayPointerDown}
            align="center"
            justify="center"
          >
            <Box id="modal-root" className={searchModalContent}>
              <Flex className={searchModalHeader} justify="between">
                <Text id="search-modal-title" className={searchModalHeaderText}>
                  Search results
                </Text>
                <Button
                  kind="ghost"
                  size="small"
                  className={searchModalClose}
                  onClick={closeModal}
                  aria-label="Close search"
                >
                  ✕
                </Button>
              </Flex>

              {results.length === 0 ? (
                <Text id="search-modal-description" className={searchNoResults}>
                  No results
                </Text>
              ) : (
                <Box id="search-modal-description">
                  {results.map((r: { sessionId: string; title: string }) => (
                    <Box
                      key={r.sessionId}
                      className={searchResultItem}
                      role="button"
                      tabIndex={0}
                      data-session-id={r.sessionId}
                      aria-label={`Open session: ${r.title}`}
                      onMouseDown={handleResultPointerDown}
                      onKeyDown={handleResultKeyDown}
                    >
                      {r.title}
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          </Flex>
        )}
      </Flex>
    </Flex>
  )
}
