import { type Locator, type Page, expect } from '@playwright/test';
import { BasePage } from '../support/page-objects/base-page';

export class LeasesPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Page container
  get homePage(): Locator {
    return this.page.getByTestId('home-page');
  }

  // Stats cards
  get statsCards(): Locator {
    return this.page.getByTestId('stats-cards');
  }

  get totalLeasesCard(): Locator {
    return this.page.getByTestId('stat-total-leases');
  }

  get totalLeasesValue(): Locator {
    return this.page.getByTestId('stat-total-leases.value');
  }

  get availableIpsCard(): Locator {
    return this.page.getByTestId('stat-available-ips');
  }

  get expiringTodayCard(): Locator {
    return this.page.getByTestId('stat-expiring-today');
  }

  get deviceTypesCard(): Locator {
    return this.page.getByTestId('stat-device-types');
  }

  // Lease table
  get leaseTable(): Locator {
    return this.page.getByTestId('lease-table');
  }

  get leaseTableLoading(): Locator {
    return this.page.getByTestId('lease-table-loading');
  }

  get leaseTableError(): Locator {
    return this.page.getByTestId('lease-table-error');
  }

  get leaseTableEmpty(): Locator {
    return this.page.getByTestId('lease-table-empty');
  }

  get leaseRows(): Locator {
    return this.page.getByTestId('lease-row');
  }

  // Table controls
  get tableControls(): Locator {
    return this.page.getByTestId('table-controls');
  }

  get searchInput(): Locator {
    return this.page.getByTestId('lease-search-input');
  }

  get searchClear(): Locator {
    return this.page.getByTestId('lease-search-clear');
  }

  get leaseCount(): Locator {
    return this.page.getByTestId('lease-count');
  }

  // Sort buttons
  sortButton(field: string): Locator {
    return this.page.getByTestId(`sort-${field}`);
  }

  // SSE status
  get sseStatus(): Locator {
    return this.page.getByTestId('sse-status');
  }

  get sseStatusDot(): Locator {
    return this.page.getByTestId('sse-status-dot');
  }

  get sseStatusLabel(): Locator {
    return this.page.getByTestId('sse-status-label');
  }

  // Actions
  async gotoLeases(): Promise<void> {
    await this.page.goto('/');
    await expect(this.leaseTable).toBeVisible({ timeout: 30_000 });
  }

  async search(term: string): Promise<void> {
    await this.searchInput.fill(term);
  }

  async clearSearch(): Promise<void> {
    await this.searchClear.click();
  }

  async clickSort(field: string): Promise<void> {
    await this.sortButton(field).click();
  }

  async getRowCount(): Promise<number> {
    return this.leaseRows.count();
  }

  async getColumnValues(testId: string): Promise<string[]> {
    const cells = this.page.getByTestId(testId);
    const count = await cells.count();
    const values: string[] = [];
    for (let i = 0; i < count; i++) {
      const text = await cells.nth(i).textContent();
      values.push(text?.trim() ?? '');
    }
    return values;
  }
}
