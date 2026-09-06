/**
 * Domain-specific test selectors.
 * App-owned — add selectors for your domain pages and components here.
 */

import { testId } from './test-id';

export const leaseSelectors = {
  page: testId('home-page'),
  table: testId('lease-table'),
  tableLoading: testId('lease-table-loading'),
  tableError: testId('lease-table-error'),
  tableEmpty: testId('lease-table-empty'),
  row: testId('lease-row'),
  controls: testId('table-controls'),
  searchInput: testId('lease-search-input'),
  searchClear: testId('lease-search-clear'),
  count: testId('lease-count'),
  sseStatus: testId('sse-status'),
  sseStatusDot: testId('sse-status-dot'),
  sseStatusLabel: testId('sse-status-label'),
  stats: {
    container: testId('stats-cards'),
    totalLeases: testId('stat-total-leases'),
    availableIps: testId('stat-available-ips'),
    expiringToday: testId('stat-expiring-today'),
    deviceTypes: testId('stat-device-types'),
  },
  sort: {
    ipAddress: testId('sort-ip_address'),
    macAddress: testId('sort-mac_address'),
    hostname: testId('sort-hostname'),
    vendor: testId('sort-vendor'),
    leaseTime: testId('sort-lease_time'),
    status: testId('sort-is_active'),
  },
};
