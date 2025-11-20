// Centralized z-index tokens for consistent stacking order across the app.
// Use these named tokens instead of hard-coded numbers to make intent clear
// and to make future adjustments safer.
export const zIndex = {
  // Lowest / base stacking
  base: 1,
  low: 2,

  // Small popovers / dropdowns / suggestion lists
  dropdown: 10,

  // sessionTree is a sidebar/normal panel — keep low unless it becomes a drawer
  sessionTree: 10,

  // tabs/Header/search related
  tabs: 40,
  headerSearch: 50,
  header: 60,

  // Sticky button bar in StartSessionPage (matches previous usage)
  stickyButtonBar: 999,

  // Modals / toasts / session tree (high-level overlays)
  // Modals and toasts should be ordered above normal panels
  modal: 1100,
  toast: 1200,

  // Full-screen loading overlay (highest priority)
  loading: 2000
}
