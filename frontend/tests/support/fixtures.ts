/**
 * Domain-specific test fixtures.
 * App-owned — extends infrastructure fixtures with domain page objects.
 */

/* eslint-disable react-hooks/rules-of-hooks */
import { infrastructureFixtures } from './fixtures-infrastructure';
import type { InfrastructureFixtures } from './fixtures-infrastructure';
import { LeasesPage } from '../dhcp/LeasesPage';

type AppFixtures = {
  leases: LeasesPage;
};

export const test = infrastructureFixtures.extend<AppFixtures>({
  leases: async ({ page }, use) => {
    await use(new LeasesPage(page));
  },
});

export type { InfrastructureFixtures };
export { expect } from '@playwright/test';
