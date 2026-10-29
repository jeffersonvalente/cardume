output "subnet_id" {
  description = "Subnet ID."
  value       = module.subnet.id
}

output "subnet_self_link" {
  description = "Subnet self link."
  value       = module.subnet.self_link
}

output "subnet_cidr" {
  description = "Primary IPv4 range."
  value       = module.subnet.ip_cidr_range
}

output "secondary_range_names" {
  description = "Secondary range names for GKE."
  value       = module.subnet.secondary_range_names
}

output "nat_ip_addresses" {
  description = "Reserved NAT egress IPs."
  value       = module.subnet.nat_ip_addresses
}
