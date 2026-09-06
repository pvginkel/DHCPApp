export interface DhcpPool {
  pool_name: string
  start_ip: string
  end_ip: string
  total_addresses: number
  lease_duration: number
  netmask: string
}
