output "id" {
  description = "Fully qualified subnet ID."
  value       = google_compute_subnetwork.this.id
}

output "name" {
  description = "Subnet name."
  value       = google_compute_subnetwork.this.name
}

output "self_link" {
  description = "Subnet self link."
  value       = google_compute_subnetwork.this.self_link
}

output "ip_cidr_range" {
  description = "Primary IPv4 range."
  value       = google_compute_subnetwork.this.ip_cidr_range
}

output "secondary_range_names" {
  description = "Names of the secondary ranges, useful for the GKE ip_allocation_policy."
  value       = keys(var.secondary_ranges)
}

output "nat_ip_addresses" {
  description = "Static external IPs reserved for NAT, empty when NAT allocates automatically."
  value       = [for address in google_compute_address.nat : address.address]
}
