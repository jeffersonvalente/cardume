output "id" {
  description = "Cluster ID."
  value       = google_container_cluster.this.id
}

output "name" {
  description = "Cluster name, used by node pools and kubectl contexts."
  value       = google_container_cluster.this.name
}

output "location" {
  description = "Region or zone of the control plane."
  value       = google_container_cluster.this.location
}

output "endpoint" {
  description = "Control plane endpoint."
  value       = google_container_cluster.this.endpoint
  sensitive   = true
}

output "ca_certificate" {
  description = "Base64-encoded cluster CA certificate."
  value       = google_container_cluster.this.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "pods_cidr" {
  description = "IPv4 range assigned to pods."
  value       = google_container_cluster.this.ip_allocation_policy[0].cluster_ipv4_cidr_block
}

output "services_cidr" {
  description = "IPv4 range assigned to services."
  value       = google_container_cluster.this.ip_allocation_policy[0].services_ipv4_cidr_block
}

output "master_cidr" {
  description = "Control plane range for private clusters, null otherwise."
  value       = one(google_container_cluster.this.private_cluster_config[*].master_ipv4_cidr_block)
}
