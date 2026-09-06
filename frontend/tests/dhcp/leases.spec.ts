import { test, expect } from '../support/fixtures';

test.describe('DHCP Leases', () => {
  test.describe('Lease Table', () => {
    test('displays lease table with data from backend', async ({ leases }) => {
      await leases.gotoLeases();

      await expect(leases.leaseTable).toBeVisible();
      await expect(leases.leaseRows.first()).toBeVisible();

      const rowCount = await leases.getRowCount();
      expect(rowCount).toBeGreaterThan(0);
    });

    test('shows all expected columns', async ({ leases }) => {
      await leases.gotoLeases();

      await expect(leases.sortButton('ip_address')).toBeVisible();
      await expect(leases.sortButton('mac_address')).toBeVisible();
      await expect(leases.sortButton('hostname')).toBeVisible();
      await expect(leases.sortButton('vendor')).toBeVisible();
      await expect(leases.sortButton('lease_time')).toBeVisible();
      await expect(leases.sortButton('is_active')).toBeVisible();
    });

    test('displays known hostnames from test data', async ({ leases }) => {
      await leases.gotoLeases();

      const hostnames = await leases.getColumnValues('lease-hostname');
      // Test data includes known hostnames from dnsmasq.leases
      const knownHostnames = ['PC-Pieter', 'Laptop-Pieter', 'kobo'];
      for (const hostname of knownHostnames) {
        expect(hostnames).toContain(hostname);
      }
    });

    test('displays IP addresses in table cells', async ({ leases }) => {
      await leases.gotoLeases();

      const ips = await leases.getColumnValues('lease-ip');
      expect(ips.length).toBeGreaterThan(0);
      // All test data IPs are in the 10.x.x.x range
      for (const ip of ips) {
        expect(ip).toMatch(/^10\.\d+\.\d+\.\d+$/);
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('filters leases by hostname', async ({ leases }) => {
      await leases.gotoLeases();

      const initialCount = await leases.getRowCount();

      await leases.search('Pieter');

      const filteredCount = await leases.getRowCount();
      expect(filteredCount).toBeLessThan(initialCount);
      expect(filteredCount).toBeGreaterThan(0);

      // Verify result count text updates
      await expect(leases.leaseCount).toContainText(`${filteredCount}`);
    });

    test('filters leases by IP address', async ({ leases }) => {
      await leases.gotoLeases();

      await leases.search('10.1.1.97');

      const filteredCount = await leases.getRowCount();
      expect(filteredCount).toBe(1);

      const ips = await leases.getColumnValues('lease-ip');
      expect(ips).toContain('10.1.1.97');
    });

    test('clears search and restores all results', async ({ leases }) => {
      await leases.gotoLeases();

      const initialCount = await leases.getRowCount();

      await leases.search('Pieter');
      const filteredCount = await leases.getRowCount();
      expect(filteredCount).toBeLessThan(initialCount);

      await leases.clearSearch();

      const restoredCount = await leases.getRowCount();
      expect(restoredCount).toBe(initialCount);
    });

    test('shows empty result when no matches', async ({ leases }) => {
      await leases.gotoLeases();

      await leases.search('zzz-nonexistent-device-zzz');

      await expect(leases.leaseTableEmpty).toBeVisible();
    });
  });

  test.describe('Column Sorting', () => {
    test('sorts by IP address ascending', async ({ leases }) => {
      await leases.gotoLeases();

      await leases.clickSort('ip_address');

      const ips = await leases.getColumnValues('lease-ip');
      expect(ips.length).toBeGreaterThan(1);

      // Verify IPs are sorted numerically (ascending)
      for (let i = 1; i < ips.length; i++) {
        const prev = ips[i - 1].split('.').map(Number);
        const curr = ips[i].split('.').map(Number);
        const prevNum = prev[0] * 16777216 + prev[1] * 65536 + prev[2] * 256 + prev[3];
        const currNum = curr[0] * 16777216 + curr[1] * 65536 + curr[2] * 256 + curr[3];
        expect(currNum).toBeGreaterThanOrEqual(prevNum);
      }
    });

    test('toggles sort direction on repeated clicks', async ({ leases }) => {
      await leases.gotoLeases();

      // First click: ascending
      await leases.clickSort('ip_address');
      const ascIps = await leases.getColumnValues('lease-ip');

      // Second click: descending
      await leases.clickSort('ip_address');
      const descIps = await leases.getColumnValues('lease-ip');

      // The order should be reversed
      expect(descIps[0]).not.toBe(ascIps[0]);
    });
  });

  test.describe('Stats Cards', () => {
    test('displays all four stat cards', async ({ leases }) => {
      await leases.gotoLeases();

      await expect(leases.statsCards).toBeVisible();
      await expect(leases.totalLeasesCard).toBeVisible();
      await expect(leases.availableIpsCard).toBeVisible();
      await expect(leases.expiringTodayCard).toBeVisible();
      await expect(leases.deviceTypesCard).toBeVisible();
    });

    test('shows numeric total leases count', async ({ leases }) => {
      await leases.gotoLeases();

      await expect(leases.totalLeasesValue).toBeVisible();
      const value = await leases.totalLeasesValue.textContent();
      const numericValue = parseInt(value ?? '', 10);
      expect(numericValue).not.toBeNaN();
    });
  });

  test.describe('SSE Connection Status', () => {
    test('shows SSE connection status indicator', async ({ leases }) => {
      await leases.gotoLeases();

      await expect(leases.sseStatus).toBeVisible();
      await expect(leases.sseStatusLabel).toBeVisible();
    });

    test('shows connected status when SSE is active', async ({ leases, deploymentSse }) => {
      await leases.gotoLeases();

      await deploymentSse.ensureConnected({ timeout: 35_000 });

      await expect(leases.sseStatusLabel).toHaveText('Live');
    });
  });
});
