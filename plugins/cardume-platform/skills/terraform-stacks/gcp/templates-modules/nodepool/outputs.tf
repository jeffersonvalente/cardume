output "id" {
  description = "Node pool ID."
  value       = google_container_node_pool.this.id
}

output "name" {
  description = "Node pool name."
  value       = google_container_node_pool.this.name
}

output "instance_group_urls" {
  description = "Managed instance groups backing the pool."
  value       = google_container_node_pool.this.managed_instance_group_urls
}
