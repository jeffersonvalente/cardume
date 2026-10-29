output "host" {
  description = "Private IP clients connect to."
  value       = google_redis_instance.this.host
}

output "port" {
  description = "TLS port."
  value       = google_redis_instance.this.port
}

output "server_ca_certs" {
  description = "CA certificates clients use to verify the TLS connection."
  value       = google_redis_instance.this.server_ca_certs
  sensitive   = true
}

output "auth_string" {
  description = "AUTH string. Store it in Secret Manager rather than passing it around in outputs."
  value       = google_redis_instance.this.auth_string
  sensitive   = true
}
