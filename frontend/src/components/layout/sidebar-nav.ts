/**
 * Navigation items for the DHCP Monitor application.
 */

import { Network } from 'lucide-react'
import type { SidebarItem } from './sidebar'

export const navigationItems: SidebarItem[] = [
  { to: '/', label: 'Leases', icon: Network, testId: 'leases' },
]
