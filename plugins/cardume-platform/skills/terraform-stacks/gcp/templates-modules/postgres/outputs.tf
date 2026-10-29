output "name" {
  description = "Instance name."
  value       = google_sql_database_instance.this.name
}

output "connection_name" {
  description = "project:region:instance string used by the Cloud SQL connectors."
  value       = google_sql_database_instance.this.connection_name
}

output "psc_service_attachment_link" {
  description = "Service attachment that consumer projects target with a PSC endpoint."
  value       = google_sql_database_instance.this.psc_service_attachment_link
}

output "dns_name" {
  description = "DNS name to use with the PSC endpoint."
  value       = google_sql_database_instance.this.dns_name
}
