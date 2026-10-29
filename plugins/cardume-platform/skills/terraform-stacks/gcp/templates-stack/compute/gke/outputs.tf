output "cluster_name" {
  description = "Cluster name."
  value       = module.cluster.name
}

output "cluster_location" {
  description = "Control plane location."
  value       = module.cluster.location
}

output "cluster_endpoint" {
  description = "Control plane endpoint."
  value       = module.cluster.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Cluster CA certificate."
  value       = module.cluster.ca_certificate
  sensitive   = true
}

output "pods_cidr" {
  description = "Pod IPv4 range."
  value       = module.cluster.pods_cidr
}

output "services_cidr" {
  description = "Service IPv4 range."
  value       = module.cluster.services_cidr
}

output "master_cidr" {
  description = "Control plane range."
  value       = module.cluster.master_cidr
}

output "node_pool_name" {
  description = "Node pool name."
  value       = module.node_pool.name
}
