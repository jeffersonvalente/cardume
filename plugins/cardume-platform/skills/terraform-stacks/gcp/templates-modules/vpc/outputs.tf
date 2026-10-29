output "id" {
  description = "Fully qualified network ID."
  value       = google_compute_network.this.id
}

output "name" {
  description = "Network name."
  value       = google_compute_network.this.name
}

output "self_link" {
  description = "Network self link, accepted by subnet, firewall and GKE resources."
  value       = google_compute_network.this.self_link
}
