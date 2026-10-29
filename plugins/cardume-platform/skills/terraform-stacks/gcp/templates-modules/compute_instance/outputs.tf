output "id" {
  description = "Instance ID."
  value       = google_compute_instance.this.id
}

output "self_link" {
  description = "Instance self link."
  value       = google_compute_instance.this.self_link
}

output "internal_ip" {
  description = "Primary internal IP address."
  value       = google_compute_instance.this.network_interface[0].network_ip
}

output "external_ip" {
  description = "Ephemeral external IP, null when none is attached."
  value       = one(google_compute_instance.this.network_interface[0].access_config[*].nat_ip)
}
